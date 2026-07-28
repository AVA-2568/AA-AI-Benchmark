#!/usr/bin/env python3
"""解析 AA leaderboard 数据 → CSV。

三级解析链（按优先级降级）：
1. RSC 数据流（scripts/aa_providers.rsc，由 build.py 带 ``RSC: 1`` 头抓取，
   ~2.4MB 纯数据，无 HTML 壳，json.JSONDecoder().raw_decode 直接解析）
2. 整页 HTML 的 __next_f.push 序列化（scripts/aa_providers.html，App Router 流式注水）
3. 整页 HTML 的 __NEXT_DATA__ script 标签（Pages Router 遗留，2026-07 已确认
   AA 迁移后不再出现，保留仅作历史回退）

解析成功后过数据哨兵（行数 + 评分字段非空率），不达标直接失败，
避免半残数据静默污染下游评分。
"""
import re, json, csv, os, sys

BS = chr(92)
OUT = os.path.dirname(os.path.abspath(__file__))
RSC_PATH = os.path.join(OUT, "aa_providers.rsc")
HTML_PATH = os.path.join(OUT, "aa_providers.html")


# ---------- 解析器 ----------

def _decode_rows_at(text, start):
    """从 text 的 '"rows":[' 处用标准库 raw_decode 解析出 rows 数组。"""
    i = text.index("[", start)
    try:
        rows, _ = json.JSONDecoder().raw_decode(text, i)
    except (json.JSONDecodeError, ValueError):
        return None
    if isinstance(rows, list) and rows and isinstance(rows[0], dict):
        return rows
    return None


def extract_via_rsc(path):
    """主路径：RSC 数据流。payload 是明文 JSON，无需反转义。"""
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    best = None
    start = text.find('"rows":[')
    while start != -1:
        rows = _decode_rows_at(text, start)
        # 页面可能有多个 rows（如小型侧表），取最长且元素含 label 的那个
        if rows and "label" in rows[0] and (best is None or len(rows) > len(best)):
            best = rows
        start = text.find('"rows":[', start + 1)
    return best


def extract_via_next_f_push(path):
    """回退 1：整页 HTML 的 __next_f.push 序列化（JS 字符串，需反转义）。"""
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", errors="replace") as f:
        html = f.read()
    pat = re.compile(
        r'self\.__next_f\.push\(\s*\[1,\s*"(.*?)"\s*\]\s*\)', re.S
    )
    chunks = pat.findall(html)
    if not chunks:
        return None
    combined = "".join(chunks).encode().decode("unicode_escape")
    start = combined.find('"rows":[')
    if start == -1:
        return None
    return _decode_rows_at(combined, start)


def extract_via_next_data(path):
    """回退 2：__NEXT_DATA__ script 标签（Pages Router 遗留）。"""
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", errors="replace") as f:
        html = f.read()
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

    def find_rows(obj, depth=0):
        if depth > 12:
            return None
        if isinstance(obj, list) and len(obj) > 100:
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


# ---------- 主解析（三级降级链） ----------
PARSERS = [
    ("RSC stream", lambda: extract_via_rsc(RSC_PATH)),
    ("__next_f.push", lambda: extract_via_next_f_push(HTML_PATH)),
    ("__NEXT_DATA__", lambda: extract_via_next_data(HTML_PATH)),
]

rows, parser_used = None, None
for name, fn in PARSERS:
    rows = fn()
    if rows:
        parser_used = name
        break
    print(f"⚠ {name} 未命中，尝试下一级")

if not rows:
    print("FATAL: 全部解析方式失败（RSC / __next_f.push / __NEXT_DATA__）")
    sys.exit(1)


# ---------- 数据哨兵 ----------
# 行数门槛：近期快照 ~1080 行，<800 视为页面结构变化或数据截断
MIN_ROWS = 800
# 评分字段（9 个通用榜 + 2 个文本榜新列）非空率哨兵：
# 均值门槛拦"整体塌方"，单字段门槛拦"某列静默消失"
SENTINEL_FIELDS = [
    "gdpvalNormalized", "terminalbenchHard", "terminalbenchV21", "scicode",
    "lcr", "omniscience", "ifbench", "gpqa", "hle",
    "omniscienceAccuracy", "omniscienceNonHallucination",
]
MEAN_RATE_MIN = 0.60   # 11 字段平均非空率下限（2026-07 实测 87%，留波动余量）
FIELD_RATE_MIN = 0.05  # 单字段非空率下限（=0 说明该列已从页面消失）

assert len(rows) > MIN_ROWS, (
    f"行数哨兵触发：{len(rows)}（预期 >{MIN_ROWS}），页面结构可能已变化"
)
for key in ("label", "model"):
    missing = sum(1 for r in rows if key not in r)
    assert missing == 0, f"{missing} 行缺少字段 '{key}'"

rates = {}
for f_ in SENTINEL_FIELDS:
    n_ok = sum(
        1 for r in rows
        if isinstance(r.get("model"), dict) and r["model"].get(f_) is not None
    )
    rates[f_] = n_ok / len(rows)
mean_rate = sum(rates.values()) / len(rates)

print(f"rows: {len(rows)}  (parser: {parser_used})")
print("字段非空率（全池）: " + ", ".join(
    f"{k}={v:.0%}" for k, v in rates.items()))
print(f"均值={mean_rate:.0%}")

bad = [k for k, v in rates.items() if v < FIELD_RATE_MIN]
assert not bad, f"字段哨兵触发：{bad} 非空率 <{FIELD_RATE_MIN:.0%}，该列可能已从页面消失"
assert mean_rate >= MEAN_RATE_MIN, (
    f"均值哨兵触发：评分字段平均非空率 {mean_rate:.0%} < {MEAN_RATE_MIN:.0%}"
)

# ---------- 字段映射 ----------
known_perf = {"medianOutputTokensPerSecond", "percentile05OutputTokensPerSec"}
extra_perf = sorted({
    k for r in rows
    for k in (r.get("performance") or {})
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
