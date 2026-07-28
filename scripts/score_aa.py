#!/usr/bin/env python3
"""Scoring engine: rank deduped models by custom weights (multi-leaderboard).

Reads config.json (leaderboards: general / text / ...); imputes missing
values ONCE over the shared imputation pool via multi-variate ridge
regression (cross-feature only, no Intelligence Index), then scores each
leaderboard with its own category weights. Outputs one CSV + one
validation JSON per leaderboard, with * markers for imputed values.
"""
import csv, json, os, sys, datetime

import numpy as np
from sklearn.preprocessing import StandardScaler

_BASE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_BASE)
SRC = os.path.join(_BASE, "aa_providers_dedup.csv")
RESULTS_DIR = os.path.join(REPO_ROOT, "results")


# ---- load config ----
config_path = os.path.join(REPO_ROOT, "config.json")
if not os.path.exists(config_path):
    print("FATAL: config.json not found (required since dual-leaderboard rework)")
    sys.exit(1)
with open(config_path, encoding="utf-8") as fh:
    cfg = json.load(fh)
print("loaded config.json")

POOL = cfg["imputation_pool"]          # shared imputation feature pool
N_POOL = len(POOL)
BOARDS = cfg["leaderboards"]           # {key: {title, output_csv, validation_json, categories}}

COST = cfg["cost"]
ALPHA = cfg["ridge_alpha"]
SCORE_THRESHOLD = cfg["score_threshold"]
MIN_SAMPLES = cfg["imputation_min_samples"]
STANDARDIZE = cfg.get("standardize_features", True)


def board_weights(board):
    """Return (CATS, GLOBAL weight map) for one leaderboard config."""
    cats = [(c["name"], c["weight"],
             [(m["name"], m["sub_weight"]) for m in c["metrics"]])
            for c in board["categories"]]
    glob = {}
    for _, cw, subs in cats:
        for m, sw in subs:
            glob[m] = cw * sw
    return cats, glob


# ---- config sanity checks (fail fast on bad config) ----
assert abs(COST["input_share"] + COST["output_share"] - 1.0) < 1e-6, (
    f"cost.input_share + cost.output_share must equal 1, "
    f"got {COST['input_share'] + COST['output_share']}"
)
assert 0 <= COST["cache_hit_rate"] <= 1, (
    f"cost.cache_hit_rate must be in [0, 1], got {COST['cache_hit_rate']}"
)
for bkey, board in BOARDS.items():
    cats, glob = board_weights(board)
    assert abs(sum(glob.values()) - 1.0) < 1e-9, (
        f"[{bkey}] global weights sum={sum(glob.values())}, must be 1.0"
    )
    for name, _, subs in cats:
        s = sum(sw for _, sw in subs)
        assert abs(s - 1.0) < 1e-6, (
            f"[{bkey}] category {name} sub_weight sum={s}, must be 1.0"
        )
    for m in glob:
        assert m in POOL, (
            f"[{bkey}] metric '{m}' not in imputation_pool — add it to the pool"
        )
    print(f"[{bkey}] global weights:",
          {m: round(w, 3) for m, w in glob.items()})


# ---- data loading ----
def to_float(v):
    v = (v or "").strip()
    if v in ("", "None", "null"):
        return None
    try:
        return float(v)
    except Exception:
        return None


rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
print("loaded rows:", len(rows))


# ---- per-metric stats (over the full pool) ----
stats = {}
for m in POOL:
    vals = [to_float(r.get(m)) for r in rows]
    vals = [v for v in vals if v is not None]
    if len(vals) < 2:
        print(f"FATAL: {m} effective samples {len(vals)} < 2")
        sys.exit(1)
    lo, hi = min(vals), max(vals)
    sv = sorted(vals)
    p90 = sv[min(len(sv) - 1, int(0.90 * (len(sv) - 1)))]
    p95 = sv[min(len(sv) - 1, int(0.95 * (len(sv) - 1)))]
    top50 = sv[len(sv) // 2:]
    top50mean = sum(top50) / len(top50)
    stats[m] = (lo, hi, top50mean, p90, p95)
    print(f"  {m:25} min={lo:.3f} max={hi:.3f} P95={p95:.3f} n={len(vals)}")


# ---- ridge regression imputation (shared, over the 11-metric pool) ----
raw = {m: [to_float(r.get(m)) for r in rows] for m in POOL}
cur = {m: [(v if v is not None else stats[m][2]) for v in raw[m]] for m in POOL}


def all_feat_row(i):
    """Return the full pool feature row for model i (all POOL metrics, in order)."""
    return [cur[mm][i] for mm in POOL]


# Fit one StandardScaler on the n x N_POOL raw matrix and apply it
# consistently across the 30 imputation rounds. The point is to put all
# pool metrics in z-score space; without this, Omniscience Index (range
# -12..100) and the two 0-100 Omniscience sub-scores dominate the 0-1
# metrics in X^T X and the ridge fit degenerates. We fit on N_POOL
# features (not N_POOL-1) so that to_X() can standardize the full row and
# then drop the target column inside it - this keeps fit/transform
# dimensions consistent.
if STANDARDIZE:
    X_raw_real = np.array([
        [raw[m][i] if raw[m][i] is not None else stats[m][2]
         for i in range(len(rows))]
        for m in POOL
    ], dtype=float)  # shape: N_POOL x n
    scaler = StandardScaler()
    scaler.fit(X_raw_real.T)  # fit on n x N_POOL
    print(f"standardized features: per-metric mean={scaler.mean_.round(2).tolist()}, "
          f"std={scaler.scale_.round(2).tolist()}")
else:
    scaler = None
    print("standardize_features=false (using raw X for ridge)")


def to_X(arr_pool, target_m):
    """arr_pool: n x N_POOL (all pool metrics, possibly including target_m).
    Returns the ridge design matrix:
    [1, standardized N_POOL-1 features excluding target_m]."""
    if scaler is not None:
        arr_pool = scaler.transform(arr_pool)
    target_idx = POOL.index(target_m)
    keep = np.r_[:target_idx, target_idx + 1:N_POOL]
    return np.hstack([np.ones((len(arr_pool), 1)), arr_pool[:, keep]])


imputation_quality = {}
for m in POOL:
    n_train = sum(1 for i in range(len(rows)) if raw[m][i] is not None)
    imputation_quality[m] = {"n_train": n_train}

print("\n--- iterative imputation ---")
prev = {m: list(cur[m]) for m in POOL}
stable_count = 0
max_delta = 0.0

MAX_ITERS = 100
for it in range(MAX_ITERS):
    for m in POOL:
        Xtr, ytr = [], []
        for i in range(len(rows)):
            if raw[m][i] is not None:
                Xtr.append(all_feat_row(i))
                ytr.append(raw[m][i])
        if len(Xtr) < 3:
            continue
        Xtr_arr = np.array(Xtr, dtype=float)
        ytr_arr = np.array(ytr, dtype=float)
        X1 = to_X(Xtr_arr, m)
        A = X1.T @ X1 + ALPHA * np.eye(X1.shape[1])
        try:
            beta = np.linalg.solve(A, X1.T @ ytr_arr)
        except np.linalg.LinAlgError:
            beta = np.linalg.lstsq(X1, ytr_arr, rcond=None)[0]
        lo, hi, _, _, p95 = stats[m]
        n_train = imputation_quality[m]["n_train"]
        for i in range(len(rows)):
            if raw[m][i] is None:
                if n_train >= MIN_SAMPLES:
                    xi = to_X(np.array([all_feat_row(i)], dtype=float), m)[0]
                    pred = max(lo, min(p95, float(xi @ beta)))
                    # 阻尼更新：抑制强相关列（如 Omniscience 三列）互预测时
                    # 的 ping-pong 振荡，加速收敛
                    cur[m][i] = 0.5 * cur[m][i] + 0.5 * pred

    # 收敛判据用「按指标量程归一的相对 delta」：绝对 delta 对量纲
    # -85..40 的 Omniscience Index 过苛（0.001 = 量程的 0.0008%）。
    # 容差 0.005（量程的 0.5%）：Omniscience 三列彼此 R²≈0.98-0.99 强耦合，
    # 迭代谱半径接近 1，收敛尾巴很长（实测 30 轮 0.0105 → 100 轮 0.0020）；
    # 0.5% 量程对应归一分 ≤0.5、加权后对总分影响 ≤0.12 分，
    # 远小于填补本身的 LOO MAE，不值得为它烧迭代轮数。
    REL_TOL = 0.005
    max_delta = 0.0
    for m in POOL:
        lo, hi = stats[m][0], stats[m][1]
        rng = (hi - lo) or 1.0
        for i in range(len(rows)):
            if raw[m][i] is None:
                max_delta = max(
                    max_delta, abs(cur[m][i] - prev[m][i]) / rng)
    if max_delta < REL_TOL:
        stable_count += 1
        if stable_count >= 3:
            print(f"  converged at iter {it - 1}, max_delta={max_delta:.6f}")
            break
    else:
        stable_count = 0
    prev = {m: list(cur[m]) for m in POOL}
else:
    print(f"  !! WARNING: not converged after {MAX_ITERS} iters, "
          f"max_delta={max_delta:.4f}")


# ---- leave-one-out validation (pool-level, computed once) ----
# Use the full set of observed samples (no subsample) so that the reported
# `n` field matches the denominator used to compute MAE and pct_over10.
print("\n--- LOO validation ---")
validation = {}
for target_m in POOL:
    has_true = [j for j in range(len(rows)) if raw[target_m][j] is not None]
    n = len(has_true)
    if n < 10:
        print(f"  {target_m}: samples too few ({n}), skip validation")
        validation[target_m] = {"mae": None, "pct_over10": None, "n": n}
        continue

    errors = []
    true_vals = []
    for skip_i in has_true:
        true_val = raw[target_m][skip_i]
        Xtr, ytr = [], []
        for j in range(len(rows)):
            if j != skip_i and raw[target_m][j] is not None:
                Xtr.append(all_feat_row(j))
                ytr.append(raw[target_m][j])
        if len(Xtr) < 3:
            continue
        Xtr_arr = np.array(Xtr, dtype=float)
        ytr_arr = np.array(ytr, dtype=float)
        X1 = to_X(Xtr_arr, target_m)
        A = X1.T @ X1 + ALPHA * np.eye(X1.shape[1])
        try:
            beta = np.linalg.solve(A, X1.T @ ytr_arr)
        except np.linalg.LinAlgError:
            beta = np.linalg.lstsq(X1, ytr_arr, rcond=None)[0]
        xi = to_X(np.array([all_feat_row(skip_i)], dtype=float), target_m)[0]
        pred = float(xi @ beta)
        lo, hi, _, _, p95 = stats[target_m]
        pred = max(lo, min(p95, pred))
        errors.append(abs(pred - true_val))
        true_vals.append(true_val)

    if not errors:
        print(f"  {target_m}: validation failed")
        validation[target_m] = {"mae": None, "pct_over10": None, "n": n}
        continue

    mae = sum(errors) / len(errors)
    over10 = sum(
        1 for i, e in enumerate(errors)
        if abs(true_vals[i]) > 0.001 and e / abs(true_vals[i]) > 0.10
    )
    validation[target_m] = {
        "mae": round(mae, 4),
        "pct_over10": round(over10 / len(errors) * 100, 1),
        "n": n,
    }
    err_pct = over10 / len(errors) * 100
    print(f"  {target_m:25} MAE={mae:.3f}  err>10%: {over10}/{len(errors)} ({err_pct:.0f}%)")

os.makedirs(RESULTS_DIR, exist_ok=True)
for bkey, board in BOARDS.items():
    _, glob = board_weights(board)
    board_val = {m: validation[m] for m in glob if m in validation}
    val_path = os.path.join(RESULTS_DIR, board["validation_json"])
    with open(val_path, "w", encoding="utf-8") as fh:
        json.dump(board_val, fh, ensure_ascii=False, indent=2)
    print(f"Saved validation [{bkey}] -> {val_path}")


# ---- scoring (per leaderboard) ----
def norm(m, v):
    lo, hi, _, _, _ = stats[m]
    if hi == lo:
        return 50.0
    return (v - lo) / (hi - lo) * 100.0


INPUT_SHARE = COST["input_share"]
OUTPUT_SHARE = COST["output_share"]
CACHE_SHARE = COST["cache_hit_rate"]


def fmt_val(val, is_imputed, is_low):
    s = str(round(val, 3))
    if is_low:
        return s + "**"
    if is_imputed:
        return s + "*"
    return s


def score_board(bkey, board):
    cats, glob = board_weights(board)
    metrics = list(glob.keys())

    out = []
    for i, r in enumerate(rows):
        eff = {}
        imputed = []
        for m in metrics:
            if raw[m][i] is not None:
                eff[m] = raw[m][i]
            else:
                n_train = imputation_quality[m]["n_train"]
                eff[m] = cur[m][i]
                if n_train < MIN_SAMPLES:
                    imputed.append(m + "(low)")
                else:
                    imputed.append(m)

        nrm = {m: norm(m, eff[m]) for m in metrics}
        total = sum(glob[m] * nrm[m] for m in metrics)

        pin = to_float(r.get("Price 1M Input"))
        pout = to_float(r.get("Price 1M Output"))
        pcache = to_float(r.get("Cache Hit Price"))
        # Industry standard: cached tokens are ~10% of input price. Fall back
        # to that when the provider does not publish a separate cache hit
        # price (most do not).
        pcache_eff = pcache if pcache is not None else (
            pin * 0.1 if pin is not None else None)
        if None in (pin, pout):
            cost_total = None
        else:
            cost_in = INPUT_SHARE * (1 - CACHE_SHARE) * pin
            cost_cache = INPUT_SHARE * CACHE_SHARE * pcache_eff
            cost_out = OUTPUT_SHARE * pout
            cost_total = round(cost_in + cost_cache + cost_out, 3)

        imputed_set = {m.split("(low)")[0] for m in imputed}
        low_set = {m.split("(low)")[0] for m in imputed if m.endswith("(low)")}

        out.append({
            "Model": r.get("Model"),
            "Creator": r.get("Creator"),
            "Reasoning": r.get("Reasoning Model"),
            "Orig Intelligence Index": to_float(r.get("Intelligence Index")),
            **{m: fmt_val(eff[m], m in imputed_set, m in low_set)
               for m in metrics},
            **{m + " (norm)": round(nrm[m], 1) for m in metrics},
            "Weighted Total": round(total, 1),
            "Price 1M In": pin,
            "Price 1M Out": pout,
            "Cache Hit": pcache_eff,
            "Total $/1M": cost_total,
            "Imputed": ", ".join(
                f"{m}(reg)" if not m.endswith("(low)")
                else f"{m[:-5]}(reg,low)"
                for m in imputed
            ) if imputed else "",
        })

    out.sort(key=lambda x: (
        x["Weighted Total"] if x["Weighted Total"] is not None else -1
    ), reverse=True)

    out = [r for r in out
           if r["Weighted Total"] is not None
           and r["Weighted Total"] >= SCORE_THRESHOLD]

    print(f"[{bkey}] >={SCORE_THRESHOLD} score: {len(out)} rows")

    for idx, row in enumerate(out, 1):
        row["Rank"] = idx

    headers = ["Rank", "Model", "Weighted Total", "Total $/1M", "Creator",
               "Reasoning", "Orig Intelligence Index"]
    for _, _, subs in cats:
        for m, _ in subs:
            headers.append(m)
            headers.append(m + " (norm)")
    headers += ["Price 1M In", "Price 1M Out", "Cache Hit", "Imputed"]

    out_csv = os.path.join(RESULTS_DIR, board["output_csv"])
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=headers, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    print(f"Saved [{bkey}] -> {out_csv}")
    return len(out)


for bkey, board in BOARDS.items():
    score_board(bkey, board)


# ---- R2 log ----
print(f"\nData snapshot: {datetime.date.today().isoformat()}")
print(f"Training R2 (no II, {N_POOL - 1}->1 cross-predict over shared pool):")
for m in POOL:
    Xtr, ytr = [], []
    for i in range(len(rows)):
        if raw[m][i] is not None:
            Xtr.append(all_feat_row(i))
            ytr.append(raw[m][i])
    if len(Xtr) < 3:
        print(f"  {m}: too few samples, skip")
        continue
    Xtr_arr = np.array(Xtr, dtype=float)
    ytr_arr = np.array(ytr, dtype=float)
    X1 = to_X(Xtr_arr, m)
    beta = np.linalg.lstsq(X1, ytr_arr, rcond=None)[0]
    pred = X1 @ beta
    ybar = ytr_arr.mean()
    ss_tot = ((ytr_arr - ybar) ** 2).sum() or 1e-12
    ss_res = ((ytr_arr - pred) ** 2).sum()
    r2 = max(0.0, 1 - ss_res / ss_tot)
    print(f"  {m:25} R2={r2:.3f}")

print("\nDONE")
