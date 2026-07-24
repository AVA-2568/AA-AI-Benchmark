#!/usr/bin/env python3
"""评分引擎：去重后的模型按自定义权重重算综合分。

读取 config.json 获取权重与参数；缺失值用多变量岭回归填补（交叉特征、不含 II）。
输出 CSV（程序用）+ Markdown（人看），填补值带 * 标记。
"""
import csv, json, math, os, sys, datetime

import numpy as np

_BASE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_BASE)
SRC = os.path.join(_BASE, "aa_providers_dedup.csv")
OUT_CSV = os.path.join(REPO_ROOT, "results", "aa_providers_scored.csv")
OUT_MD = os.path.join(REPO_ROOT, "results", "ranking.md")
OUT_VAL = os.path.join(REPO_ROOT, "results", "validation.json")


# ---- 加载配置 ----
config_path = os.path.join(REPO_ROOT, "config.json")
if os.path.exists(config_path):
    with open(config_path, encoding="utf-8") as fh:
        cfg = json.load(fh)
    print("loaded config.json")
else:
    cfg = {
        "categories": [
            {"name": "智能体 Agentic", "weight": 0.20,
             "metrics": [{"name": "GDPval-AA", "sub_weight": 1.00}]},
            {"name": "编程 Coding", "weight": 0.20, "metrics": [
                {"name": "Terminal-Bench Hard", "sub_weight": 0.50},
                {"name": "Terminal-Bench v2.1", "sub_weight": 0.30},
                {"name": "SciCode", "sub_weight": 0.20}]},
            {"name": "通用 General", "weight": 0.40, "metrics": [
                {"name": "LCR", "sub_weight": 0.30},
                {"name": "Omniscience Index", "sub_weight": 0.30},
                {"name": "IFBench", "sub_weight": 0.40}]},
            {"name": "知识 Knowledge", "weight": 0.20, "metrics": [
                {"name": "GPQA Diamond", "sub_weight": 0.40},
                {"name": "HLE", "sub_weight": 0.60}]},
        ],
        "cost": {"input_share": 0.70, "output_share": 0.30, "cache_hit_rate": 0.50},
        "score_threshold": 70,
        "ridge_alpha": 1.0,
        "imputation_min_samples": 50,
    }
    print("config.json not found, using built-in defaults")

CATS = [(c["name"], c["weight"], [(m["name"], m["sub_weight"]) for m in c["metrics"]])
        for c in cfg["categories"]]
METRICS = [m for _, _, subs in CATS for m, _ in subs]
GLOBAL = {}
for _, cw, subs in CATS:
    for m, sw in subs:
        GLOBAL[m] = cw * sw
assert abs(sum(GLOBAL.values()) - 1.0) < 1e-9, f"weights sum={sum(GLOBAL.values())}, must be 1.0"
print("global weights:", {m: round(GLOBAL[m], 3) for m in METRICS})

COST = cfg["cost"]
ALPHA = cfg["ridge_alpha"]
SCORE_THRESHOLD = cfg["score_threshold"]
MIN_SAMPLES = cfg["imputation_min_samples"]


# ---- 数据加载 ----
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


# ---- 每指标统计 ----
stats = {}
for m in METRICS:
    vals = [to_float(r.get(m)) for r in rows]
    vals = [v for v in vals if v is not None]
    if len(vals) < 2:
        print(f"FATAL: {m} 有效样本数 {len(vals)} < 2")
        sys.exit(1)
    lo, hi = min(vals), max(vals)
    sv = sorted(vals)
    p90 = sv[min(len(sv) - 1, int(0.90 * (len(sv) - 1)))]
    p95 = sv[min(len(sv) - 1, int(0.95 * (len(sv) - 1)))]
    top50 = sv[len(sv) // 2:]
    top50mean = sum(top50) / len(top50)
    stats[m] = (lo, hi, top50mean, p90, p95)
    print(f"  {m:20} min={lo:.3f} max={hi:.3f} P95={p95:.3f} n={len(vals)}")


# ---- 岭回归填补 ----
raw = {m: [to_float(r.get(m)) for r in rows] for m in METRICS}
cur = {m: [(v if v is not None else stats[m][2]) for v in raw[m]] for m in METRICS}


def feat(i, target):
    return [cur[mm][i] for mm in METRICS if mm != target]


imputation_quality = {}
for m in METRICS:
    n_train = sum(1 for i in range(len(rows)) if raw[m][i] is not None)
    imputation_quality[m] = {"n_train": n_train}

print("\n--- 迭代填补 ---")
prev = {m: list(cur[m]) for m in METRICS}
stable_count = 0

for it in range(30):
    for m in METRICS:
        Xtr, ytr = [], []
        for i in range(len(rows)):
            if raw[m][i] is not None:
                Xtr.append(feat(i, m))
                ytr.append(raw[m][i])
        if len(Xtr) < 3:
            continue
        Xtr_arr = np.array(Xtr, dtype=float)
        ytr_arr = np.array(ytr, dtype=float)
        X1 = np.hstack([np.ones((len(Xtr_arr), 1)), Xtr_arr])
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
                    xi = np.array([1.0] + feat(i, m))
                    pred = float(xi @ beta)
                    cur[m][i] = max(lo, min(p95, pred))

    max_delta = 0.0
    for m in METRICS:
        for i in range(len(rows)):
            if raw[m][i] is None:
                max_delta = max(max_delta, abs(cur[m][i] - prev[m][i]))
    if max_delta < 0.001:
        stable_count += 1
        if stable_count >= 3:
            print(f"  收敛于第 {it - 1} 轮，max_delta={max_delta:.6f}")
            break
    else:
        stable_count = 0
    prev = {m: list(cur[m]) for m in METRICS}
else:
    print(f"  ⚠ 警告：30 轮未收敛，max_delta={max_delta:.4f}")


# ---- 留一验证 ----
print("\n--- 留一验证 ---")
validation = {}
for target_m in METRICS:
    has_true = [j for j in range(len(rows)) if raw[target_m][j] is not None]
    n = len(has_true)
    if n < 10:
        print(f"  {target_m}: 样本不足 ({n})，跳过验证")
        validation[target_m] = {"mae": None, "pct_over10": None, "n": n}
        continue

    sample_indices = has_true
    if n > 60:
        rng = np.random.RandomState(42)
        sample_indices = list(rng.choice(has_true, 60, replace=False))

    errors = []
    true_vals = []
    for skip_i in sample_indices:
        true_val = raw[target_m][skip_i]
        Xtr, ytr = [], []
        for j in range(len(rows)):
            if j != skip_i and raw[target_m][j] is not None:
                Xtr.append(feat(j, target_m))
                ytr.append(raw[target_m][j])
        if len(Xtr) < 3:
            continue
        Xtr_arr = np.array(Xtr, dtype=float)
        ytr_arr = np.array(ytr, dtype=float)
        X1 = np.hstack([np.ones((len(Xtr_arr), 1)), Xtr_arr])
        A = X1.T @ X1 + ALPHA * np.eye(X1.shape[1])
        try:
            beta = np.linalg.solve(A, X1.T @ ytr_arr)
        except np.linalg.LinAlgError:
            beta = np.linalg.lstsq(X1, ytr_arr, rcond=None)[0]
        xi = np.array([1.0] + feat(skip_i, target_m))
        pred = float(xi @ beta)
        lo, hi, _, _, p95 = stats[target_m]
        pred = max(lo, min(p95, pred))
        errors.append(abs(pred - true_val))
        true_vals.append(true_val)

    if not errors:
        print(f"  {target_m}: 无法完成验证")
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
    print(
        f"  {target_m:25} MAE={mae:.3f}  "
        f"误差>10%: {over10}/{len(errors)} ({over10/len(errors)*100:.0f}%)"
    )

os.makedirs(os.path.dirname(OUT_VAL), exist_ok=True)
with open(OUT_VAL, "w", encoding="utf-8") as fh:
    json.dump(validation, fh, ensure_ascii=False, indent=2)
print("Saved validation ->", OUT_VAL)


# ---- 评分 ----
def norm(m, v):
    lo, hi, _, _, _ = stats[m]
    if hi == lo:
        return 50.0
    return (v - lo) / (hi - lo) * 100.0


INPUT_SHARE = COST["input_share"]
OUTPUT_SHARE = COST["output_share"]
CACHE_SHARE = COST["cache_hit_rate"]


def fmt_val(val, is_imputed, is_low):
    """填补值加 *（低可信加 **），真实值不加标记。"""
    s = str(round(val, 3))
    if is_low:
        return s + "**"
    if is_imputed:
        return s + "*"
    return s


out = []
for i, r in enumerate(rows):
    eff = {}
    imputed = []
    for m in METRICS:
        if raw[m][i] is not None:
            eff[m] = raw[m][i]
        else:
            n_train = imputation_quality[m]["n_train"]
            eff[m] = cur[m][i]
            if n_train < MIN_SAMPLES:
                imputed.append(m + "(low)")
            else:
                imputed.append(m)

    nrm = {m: norm(m, eff[m]) for m in METRICS}
    total = sum(GLOBAL[m] * nrm[m] for m in METRICS)

    pin = to_float(r.get("Price 1M Input"))
    pout = to_float(r.get("Price 1M Output"))
    pcache = to_float(r.get("Cache Hit Price"))
    pcache_eff = pcache if pcache is not None else pin
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
           for m in METRICS},
        **{m + " (norm)": round(nrm[m], 1) for m in METRICS},
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

print(f">={SCORE_THRESHOLD} 分共 {len(out)} 行")

for idx, row in enumerate(out, 1):
    row["Rank"] = idx


# ---- 写入 CSV ----
headers = ["Rank", "Model", "Weighted Total", "Total $/1M", "Creator",
           "Reasoning", "Orig Intelligence Index"]
for _, _, subs in CATS:
    for m, _ in subs:
        headers.append(m)
        headers.append(m + " (norm)")
headers += ["Price 1M In", "Price 1M Out", "Cache Hit", "Imputed"]

os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=headers, extrasaction="ignore")
    w.writeheader()
    w.writerows(out)
print("Saved", OUT_CSV)


# ---- 写入 Markdown ----
md_lines = [
    f"# AI 模型综合排名（\u2265{SCORE_THRESHOLD} 分）",
    "",
    f"> {datetime.date.today().isoformat()} 更新  |  "
    f"* 表示回归预测填补  |  ** 表示低可信填补（训练样本 < {MIN_SAMPLES}）",
    "",
]
# 紧凑表头
md_cols = ["#", "Model", "Score", "$/1M",
           "Agent", "Coding", "General", "Knowledge", "Imputed"]
md_lines.append("| " + " | ".join(md_cols) + " |")
md_lines.append("|" + "|".join(["---"] * len(md_cols)) + "|")

for r in out:
    # Agent: GDPval-AA 的原始值
    agent_val = r.get("GDPval-AA", "")
    # Coding: Terminal-Bench Hard
    coding_val = r.get("Terminal-Bench Hard", "")
    # General: LCR
    general_val = r.get("LCR", "")
    # Knowledge: HLE
    knowledge_val = r.get("HLE", "")
    imp = (r.get("Imputed") or "").strip()
    cost = r.get("Total $/1M")
    cost_str = str(cost) if cost is not None else "—"

    md_lines.append(
        f"| {r['Rank']} | {r['Model']} | {r['Weighted Total']} | "
        f"{cost_str} | {agent_val} | {coding_val} | "
        f"{general_val} | {knowledge_val} | "
        f"{imp or '—'} |"
    )

with open(OUT_MD, "w", encoding="utf-8") as fh:
    fh.write("\n".join(md_lines) + "\n")
print("Saved", OUT_MD)


# ---- R\u00b2 日志 ----
today_str = datetime.date.today().isoformat()
print(f"\nData snapshot: {today_str}, {len(out)} rows")
print("训练集 R\u00b2 (不含 II，仅 8\u21921 交叉预测):")
for m in METRICS:
    Xtr, ytr = [], []
    for i in range(len(rows)):
        if raw[m][i] is not None:
            Xtr.append(feat(i, m))
            ytr.append(raw[m][i])
    if len(Xtr) < 3:
        print(f"  {m}: 样本不足，跳过")
        continue
    Xtr_arr = np.array(Xtr, dtype=float)
    ytr_arr = np.array(ytr, dtype=float)
    X1 = np.hstack([np.ones((len(Xtr_arr), 1)), Xtr_arr])
    beta = np.linalg.lstsq(X1, ytr_arr, rcond=None)[0]
    pred = X1 @ beta
    ybar = ytr_arr.mean()
    ss_tot = ((ytr_arr - ybar) ** 2).sum() or 1e-12
    ss_res = ((ytr_arr - pred) ** 2).sum()
    r2 = max(0.0, 1 - ss_res / ss_tot)
    print(f"  {m:25} R\u00b2={r2:.3f}")

print("\nDONE")
