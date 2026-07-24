#!/usr/bin/env python3
"""解析 AA leaderboard HTML → CSV。

优先从 Next.js __NEXT_DATA__ JSON 提取（跨版本稳定），
失败时回退到 __next_f.push 内部序列化格式。
"""
import re, json, csv, os, sys

BS = chr(92)
OUT = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(OUT, "aa_providers.html")

with open(HTML_PATH, encoding="utf-8") as f:
    html = f.read()


def extract_via_next_data(html):
    """从 __NEXT_DATA__ script 标签提取 rows，失败返回 None。"""
    m = re.search(
        r'<script\s+id="__NEXT_DATA__"[^>]*>\s*(.*?)\s*</script>',
        html, re.S | re.I,
    )
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return None
    # 遍历可能的路径找到 rows 数组
    def find_rows(obj, depth=0):
        if depth > 12:
            return None
        if isinstance(obj, list) and len(obj) > 100:
            # 检查是否是模型列表（第一个元素的 label 字段存在）
            if isinstance(obj[0], dict) and "label" in obj[0]:
                return obj
        if isinstance(obj, dict):
            for v in obj.values():
                r = find_rows(v, depth + 1)
                if r is not None:
                    return r
        if isinstance(obj, list) and len(obj) < 100:
            for item in obj:
                r = find_rows(item, depth + 1)
                if r is not None:
                    return r
        return None
    return find_rows(data)


def extract_via_next_f_push(html):
    """从 __next_f.push 内部格式提取 rows（旧版回退）。"""
    pat = re.compile(
        r'self\.__next_f\.push\(\s*\[1,\s*"(.*?)"\s*\]\s*\)', re.S
    )
    combined = "".join(pat.findall(html)).encode().decode("unicode_escape")
    start = combined.find('"rows":[')
    if start == -1:
        return None
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
            elif c == BS:
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
    if end is None:
        return None
    return json.loads(combined[i:end])


# ---- 主解析 ----
rows = None
parser_used = None

rows = extract_via_next_data(html)
if rows is not None:
    parser_used = "__NEXT_DATA__"
else:
    print("⚠ __NEXT_DATA__ 未命中，回退到 __next_f.push")
    rows = extract_via_next_f_push(html)
    if rows is not None:
        parser_used = "__next_f.push"

if rows is None:
    print("FATAL: 两种解析方式均失败")
    sys.exit(1)

# ---- 校验 ----
assert len(rows) > 100, (
    f"行数异常：{len(rows)}（预期 >100），可能页面结构已变化"
)
required_keys = ["label", "model"]
for key in required_keys:
    missing = sum(1 for r in rows if key not in r)
    assert missing == 0, f"{missing} 行缺少字段 '{key}'"
print(f"rows: {len(rows)}  (parser: {parser_used})")

# ---- 字段映射 ----
known_perf = {"medianOutputTokensPerSecond", "percentile05OutputTokensPerSec"}
extra_perf = sorted({
    k for r in rows
    for k in r.get("performance", {})
    if k not in known_perf
})


def get(row, spec):
    cur = row
    for p in spec[1:]:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


cols = [
    ("Model", "label"),
    ("Host API ID", "hostApiId"),
    ("Provider", "host", "name"),
    ("Provider Slug", "host", "slug"),
    ("Model Slug", "model", "slug"),
    ("Creator", "model", "creator", "name"),
    ("Open Weights", "model", "isOpenWeights"),
    ("Deprecated", "model", "deprecated"),
    ("Reasoning Model", "model", "reasoningModel"),
    ("Intelligence Index", "model", "intelligenceIndex"),
    ("Intelligence Index Est.", "model", "intelligenceIndexIsEstimated"),
    ("Omniscience Index", "model", "omniscience"),
    ("Omniscience Accuracy", "model", "omniscienceAccuracy"),
    ("Omniscience Non-Halluc.", "model", "omniscienceNonHallucination"),
    ("GDPval-AA", "model", "gdpvalNormalized"),
    ("Terminal-Bench Hard", "model", "terminalbenchHard"),
    ("Terminal-Bench v2.1", "model", "terminalbenchV21"),
    ("tau2-Bench Telecom", "model", "tau2"),
    ("tau3-Banking", "model", "tauBanking"),
    ("LCR", "model", "lcr"),
    ("HLE", "model", "hle"),
    ("GPQA Diamond", "model", "gpqa"),
    ("SciCode", "model", "scicode"),
    ("LiveCodeBench", "model", "livecodebench"),
    ("AIME 2025", "model", "aime25"),
    ("IFBench", "model", "ifbench"),
    ("CritPt", "model", "critpt"),
    ("APEX Agents", "model", "apexAgents"),
    ("ITBench SRE", "model", "itbenchSre"),
    ("Harvey LAB", "model", "harveyLab"),
    ("AutomationBench", "model", "automationBench"),
    ("MMMU-Pro", "model", "mmmuPro"),
    ("Context Window", "features", "contextWindowTokens"),
    ("Function Calling", "features", "functionCalling"),
    ("JSON Mode", "features", "jsonMode"),
    ("OpenAI Compatible", "features", "openaiCompatible"),
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

print(f"CSV -> {csv_path}  ({len(cols)} 列)")
if extra_perf:
    print(f"🔔 发现新性能指标: {', '.join(extra_perf)}")
else:
    print("无新增性能指标")
