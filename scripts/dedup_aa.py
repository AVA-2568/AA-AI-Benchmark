import csv, os

OUT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(OUT, "aa_providers.csv")

rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
cols = list(rows[0].keys())


def score(r):
    v = r.get("Intelligence Index") or ""
    try:
        return float(v)
    except ValueError:
        return float("-inf")


# dedup by Model Slug, keep row with highest Intelligence Index
best = {}
for r in rows:
    k = r.get("Model Slug") or r.get("Model")
    if k not in best or score(r) > score(best[k]):
        best[k] = r

dedup = sorted(best.values(), key=lambda r: score(r), reverse=True)
print("before:", len(rows), "after:", len(dedup))

csv_path = os.path.join(OUT, "aa_providers_dedup.csv")
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(dedup)
print("CSV ->", csv_path)
