import re, json, csv, os
bs = chr(92)
OUT = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(OUT, "aa_providers.html"), encoding="utf-8").read()
pat = re.compile(r'self\.__next_f\.push\(\s*\[1,\s*"(.*?)"\s*\]\s*\)', re.S)
combined = "".join(pat.findall(html)).encode().decode("unicode_escape")
start = combined.find('"rows":[')
i = combined.index("[", start)
depth = 0
in_str = False
esc = False
end = None
for j in range(i, len(combined)):
    c = combined[j]
    if in_str:
        if esc:
            esc = False
        elif c == bs:
            esc = True
        elif c == '"':
            in_str = False
        continue
    if c == '"':
        in_str = True
    elif c == "[":
        depth += 1
    elif c == "]":
        depth -= 1
        if depth == 0:
            end = j + 1
            break
rows = json.loads(combined[i:end])
print("rows:", len(rows))

known_perf = {"medianOutputTokensPerSecond", "percentile05OutputTokensPerSec"}
extra_perf = sorted({k for r in rows for k in r.get("performance", {}) if k not in known_perf})


def get(row, spec):
    cur = row
    for p in spec[1:]:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


cols = [
    ("Model", "label"), ("Host API ID", "hostApiId"), ("Provider", "host", "name"),
    ("Provider Slug", "host", "slug"), ("Model Slug", "model", "slug"),
    ("Creator", "model", "creator", "name"), ("Open Weights", "model", "isOpenWeights"),
    ("Deprecated", "model", "deprecated"), ("Reasoning Model", "model", "reasoningModel"),
    ("Intelligence Index", "model", "intelligenceIndex"),
    ("Intelligence Index Est.", "model", "intelligenceIndexIsEstimated"),
    ("Omniscience Index", "model", "omniscience"),
    ("Omniscience Accuracy", "model", "omniscienceAccuracy"),
    ("Omniscience Non-Halluc.", "model", "omniscienceNonHallucination"),
    ("GDPval-AA", "model", "gdpvalNormalized"),
    ("Terminal-Bench Hard", "model", "terminalbenchHard"),
    ("Terminal-Bench v2.1", "model", "terminalbenchV21"),
    ("tau2-Bench Telecom", "model", "tau2"), ("tau3-Banking", "model", "tauBanking"),
    ("LCR", "model", "lcr"), ("HLE", "model", "hle"), ("GPQA Diamond", "model", "gpqa"),
    ("SciCode", "model", "scicode"), ("LiveCodeBench", "model", "livecodebench"),
    ("AIME 2025", "model", "aime25"), ("IFBench", "model", "ifbench"),
    ("CritPt", "model", "critpt"), ("APEX Agents", "model", "apexAgents"),
    ("ITBench SRE", "model", "itbenchSre"), ("Harvey LAB", "model", "harveyLab"),
    ("AutomationBench", "model", "automationBench"), ("MMMU-Pro", "model", "mmmuPro"),
    ("Context Window", "features", "contextWindowTokens"),
    ("Function Calling", "features", "functionCalling"),
    ("JSON Mode", "features", "jsonMode"), ("OpenAI Compatible", "features", "openaiCompatible"),
    ("Price 1M Input", "pricing", "price1mInputTokens"),
    ("Price 1M Output", "pricing", "price1mOutputTokens"),
    ("Cache Hit Price", "pricing", "cacheHitPrice"),
    ("Cache Write Price", "pricing", "cacheWritePrice"),
    ("Price Class", "pricing", "priceClass"),
    ("Median tok/s", "performance", "medianOutputTokensPerSecond"),
    ("P05 tok/s", "performance", "percentile05OutputTokensPerSec"),
]
for k in extra_perf:
    cols.append((k, "performance", k))
cols.append(("Footnotes", "footnotes"))

csv_path = os.path.join(OUT, "aa_providers.csv")
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow([c[0] for c in cols])
    for r in rows:
        w.writerow([get(r, spec) for spec in cols])
print("CSV ->", csv_path, "cols:", len(cols))

try:
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Providers"
    ws.append([c[0] for c in cols])
    for r in rows:
        ws.append([get(r, spec) for spec in cols])
    xlsx_path = os.path.join(OUT, "aa_providers.xlsx")
    wb.save(xlsx_path)
    print("XLSX ->", xlsx_path)
except Exception as e:
    print("xlsx skipped:", e)
