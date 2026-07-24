import csv, math, os, datetime

_BASE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_BASE)
SRC = os.path.join(_BASE, "aa_providers_dedup.csv")
OUT = os.path.join(REPO_ROOT, "results", "aa_providers_scored.csv")

def f(v):
    v = (v or "").strip()
    if v in ("", "None", "null"):
        return None
    try:
        return float(v)
    except Exception:
        return None

rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
print("loaded rows:", len(rows))

# ---- hierarchical weights ----
CATS = [
    ("智能体 Agentic", 0.20, [("GDPval-AA", 1.00)]),
    ("编程 Coding",    0.20, [("Terminal-Bench Hard", 0.50),
                              ("Terminal-Bench v2.1", 0.30),
                              ("SciCode", 0.20)]),
    ("通用 General",   0.40, [("LCR", 0.30),
                              ("Omniscience Index", 0.30),
                              ("IFBench", 0.40)]),
    ("知识 Knowledge",  0.20, [("GPQA Diamond", 0.40),
                              ("HLE", 0.60)]),
]
METRICS = [m for _, _, subs in CATS for m, _ in subs]
GLOBAL = {}
for _, cw, subs in CATS:
    for m, sw in subs:
        GLOBAL[m] = cw * sw
assert abs(sum(GLOBAL.values()) - 1.0) < 1e-9, "weights must sum to 1"
print("global weights:", {m: round(GLOBAL[m], 3) for m in METRICS})

# ---- per-metric stats ----
stats = {}
P95 = {}
for m in METRICS:
    vals = [f(r.get(m)) for r in rows]
    vals = [v for v in vals if v is not None]
    lo, hi = min(vals), max(vals)
    sv = sorted(vals)
    p90 = sv[min(len(sv) - 1, int(0.90 * (len(sv) - 1)))]
    p95 = sv[min(len(sv) - 1, int(0.95 * (len(sv) - 1)))]
    top50 = sorted(vals)[len(vals) // 2:]
    top50mean = sum(top50) / len(top50)
    stats[m] = (lo, hi, top50mean, p90, p95)
    P95[m] = p95
    print(f"  {m:20} min={lo:.3f} max={hi:.3f} P95={p95:.3f} n={len(vals)}")

# ---- multivariate ridge-regression imputation ----
import numpy as np
II = [f(r.get("Intelligence Index")) for r in rows]
raw = {m: [f(r.get(m)) for r in rows] for m in METRICS}
cur = {m: [(v if v is not None else stats[m][2]) for v in raw[m]] for m in METRICS}

ALPHA = 1.0
def feat(i, target):
    xs = [cur[mm][i] for mm in METRICS if mm != target]
    xs.append(0.0 if II[i] is None else II[i])
    return xs

for it in range(30):
    for m in METRICS:
        Xtr, ytr = [], []
        for i in range(len(rows)):
            if raw[m][i] is not None:
                Xtr.append(feat(i, m)); ytr.append(raw[m][i])
        Xtr = np.array(Xtr, dtype=float); ytr = np.array(ytr, dtype=float)
        X1 = np.hstack([np.ones((len(Xtr), 1)), Xtr])
        A = X1.T @ X1 + ALPHA * np.eye(X1.shape[1])
        try:
            beta = np.linalg.solve(A, X1.T @ ytr)
        except np.linalg.LinAlgError:
            beta = np.linalg.lstsq(X1, ytr, rcond=None)[0]
        lo, hi, _, _, p95 = stats[m]
        for i in range(len(rows)):
            if raw[m][i] is None:
                xi = np.array([1.0] + feat(i, m))
                pred = float(xi @ beta)
                cur[m][i] = max(lo, min(p95, pred))

def norm(m, v):
    lo, hi, _, _, _ = stats[m]
    return 0.0 if hi == lo else (v - lo) / (hi - lo) * 100.0

INPUT_SHARE, OUTPUT_SHARE = 0.70, 0.30
CACHE_SHARE = 0.50

out = []
for i, r in enumerate(rows):
    eff = {}; imputed = []
    for m in METRICS:
        if raw[m][i] is not None:
            eff[m] = raw[m][i]
        else:
            eff[m] = cur[m][i]; imputed.append(m)
    nrm = {m: norm(m, eff[m]) for m in METRICS}
    total = sum(GLOBAL[m] * nrm[m] for m in METRICS)

    pin = f(r.get("Price 1M Input"))
    pout = f(r.get("Price 1M Output"))
    pcache = f(r.get("Cache Hit Price"))
    pcache_eff = pcache if pcache is not None else pin
    if None in (pin, pout):
        cost_total = None
    else:
        cost_in = INPUT_SHARE * (1 - CACHE_SHARE) * pin
        cost_cache = INPUT_SHARE * CACHE_SHARE * pcache_eff
        cost_out = OUTPUT_SHARE * pout
        cost_total = round(cost_in + cost_cache + cost_out, 3)

    out.append({
        "Model": r.get("Model"), "Creator": r.get("Creator"),
        "Reasoning": r.get("Reasoning Model"),
        "Orig Intelligence Index": f(r.get("Intelligence Index")),
        **{m: (round(eff[m], 3) if m in imputed else raw[m][i]) for m in METRICS},
        **{m + " (norm)": round(nrm[m], 1) for m in METRICS},
        "Weighted Total": round(total, 1),
        "Price 1M In": pin, "Price 1M Out": pout, "Cache Hit": pcache_eff,
        "Total $/1M": cost_total,
        "Imputed": ", ".join(f"{m}(reg)" for m in imputed) if imputed else "",
    })

out.sort(key=lambda x: (x["Weighted Total"] if x["Weighted Total"] is not None else -1), reverse=True)

keep = math.ceil(len(out) * 0.15)
out = out[:keep]
print(f"top15% keep = {keep}")

# assign rank
for idx, row in enumerate(out, 1):
    row["Rank"] = idx

# write CSV
headers = ["Rank", "Model", "Weighted Total", "Total $/1M", "Creator", "Reasoning",
           "Orig Intelligence Index"]
for _, _, subs in CATS:
    for m, _ in subs:
        headers.append(m)
        headers.append(m + " (norm)")
headers += ["Price 1M In", "Price 1M Out", "Cache Hit", "Imputed"]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
    w.writeheader()
    w.writerows(out)
print("Saved", OUT)

# print R² for logging
today_str = datetime.date.today().isoformat()
print(f"\nData snapshot: {today_str}, {keep} rows")
R2 = {}
for m in METRICS:
    Xtr, ytr = [], []
    for i in range(len(rows)):
        if raw[m][i] is not None:
            Xtr.append(feat(i, m)); ytr.append(raw[m][i])
    Xtr = np.array(Xtr, dtype=float); ytr = np.array(ytr, dtype=float)
    X1 = np.hstack([np.ones((len(Xtr), 1)), Xtr])
    beta = np.linalg.lstsq(X1, ytr, rcond=None)[0]
    pred = X1 @ beta
    ybar = ytr.mean()
    ss_tot = ((ytr - ybar) ** 2).sum() or 1e-12
    ss_res = ((ytr - pred) ** 2).sum()
    R2[m] = max(0.0, 1 - ss_res / ss_tot)
print("R²: " + "; ".join(f"{m}={R2[m]:.2f}" for m in METRICS))
