#!/usr/bin/env python3
"""一键构建：抓取 AA leaderboard -> 解析 -> 去重 -> 评分 -> 刷新 README。

抓取策略（与 parse_aa.py 的三级解析链配套）：
1. 主路径：带 ``RSC: 1`` 头请求同一 URL，拿 RSC 数据流（~2.4MB 纯数据）
2. 回退：抓整页 HTML（~5.4MB），parse_aa.py 走 __next_f.push / __NEXT_DATA__
3. 最后手段：沿用上次运行留下的缓存文件并打警告（CI 日志可见）

可在本地运行，也可由 GitHub Actions 调用。
"""
import json
import os
import sys
import csv
import subprocess
import datetime
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE)
RSC = os.path.join(BASE, "aa_providers.rsc")
HTML = os.path.join(BASE, "aa_providers.html")
URL = "https://artificialanalysis.ai/leaderboards/providers"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

# RSC 流 2026-07 实测 ~2.4MB；小于该值大概率是错误页/挑战页
RSC_MIN_SIZE = 500_000
HTML_MIN_SIZE = 100_000


def _fetch(url, out_path, min_size, extra_headers=None):
    """curl 优先、urllib 回退的通用抓取。写临时文件成功后才覆盖目标，
    避免失败请求把上次的可用缓存冲掉。"""
    tmp = out_path + ".tmp"
    headers = {"User-Agent": UA}
    headers.update(extra_headers or {})
    try:
        cmd = ["curl", "-sL", "--max-time", "120", url, "-o", tmp]
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
        r = subprocess.run(cmd, check=False)
        if r.returncode == 0 and os.path.exists(tmp) \
                and os.path.getsize(tmp) > min_size:
            os.replace(tmp, out_path)
            print(f"fetched via curl -> {os.path.basename(out_path)}, "
                  f"size={os.path.getsize(out_path)}")
            return True
    except FileNotFoundError:
        pass
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
        if len(data) > min_size:
            with open(out_path, "wb") as f:
                f.write(data)
            print(f"fetched via urllib -> {os.path.basename(out_path)}, "
                  f"size={len(data)}")
            return True
    except Exception as e:
        print(f"urllib fetch failed: {e}")
    if os.path.exists(tmp):
        os.remove(tmp)
    return False


def fetch_data():
    """三级抓取：RSC 流 -> 整页 HTML -> 上次缓存。"""
    if _fetch(URL, RSC, RSC_MIN_SIZE, {"RSC": "1"}):
        return True
    print("!! RSC fetch failed, falling back to full HTML")
    if _fetch(URL, HTML, HTML_MIN_SIZE):
        # HTML 是新鲜的，删掉过期 RSC，防止 parse_aa.py 优先吃到旧数据
        if os.path.exists(RSC):
            os.remove(RSC)
            print("removed stale aa_providers.rsc (fresh HTML takes over)")
        return True
    if os.path.exists(RSC) or os.path.exists(HTML):
        print("!! WARNING: both fetches failed, reusing STALE cache from "
              "previous run — rankings may be outdated")
        return True
    return False


def run(script):
    subprocess.run([sys.executable, os.path.join(BASE, script)],
                   cwd=BASE, check=True)


def _count(path):
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8-sig", newline="") as f:
        return sum(1 for _ in csv.reader(f)) - 1


def _load_boards():
    with open(os.path.join(REPO_ROOT, "config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg["leaderboards"]


def _board_blocks(bkey, board, n_raw, n_dedup, today):
    """生成单个榜单的 (snapshot_md, top15_md)。"""
    scored = os.path.join(REPO_ROOT, "results", board["output_csv"])
    val_json = os.path.join(REPO_ROOT, "results", board["validation_json"])
    n_out = _count(scored)

    with open(scored, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    top = rows[:15]
    lines = [
        "| # | Model | Creator | Score | $/1M | Imputed |",
        "|---|---|---|---|---|---|",
    ]
    for r in top:
        imp = (r["Imputed"] or "").strip()
        lines.append("| {} | {} | {} | {} | {} | {} |".format(
            r["Rank"], r["Model"], r["Creator"],
            r.get("Weighted Total") or "", r.get("Total $/1M") or "",
            imp or "-",
        ))
    top15_md = "\n".join(lines)

    snapshot_parts = [
        f"> {today} 抓取"
        f"（{n_raw} 模型 x 服务商 -> 去重 {n_dedup}"
        f" -> >=70 分 {n_out} 行）。"
    ]
    if os.path.exists(val_json):
        with open(val_json, encoding="utf-8") as f:
            val = json.load(f)
        val_lines = []
        for m, v in val.items():
            if v.get("mae") is not None:
                val_lines.append(
                    f"{m} MAE={v['mae']:.2f}"
                    f" (>10%: {v['pct_over10']}%/{v['n']})"
                )
        if val_lines:
            snapshot_parts.append(f"> 填补验证：{' ; '.join(val_lines)}")

    return "\n".join(snapshot_parts), top15_md, n_out


def update_readme():
    """用最新 scored CSV 刷新 README：每个榜单一组 SNAPSHOT/TOP15 区块。"""
    raw_csv = os.path.join(BASE, "aa_providers.csv")
    dedup_csv = os.path.join(BASE, "aa_providers_dedup.csv")
    today = datetime.date.today().isoformat()
    n_raw = _count(raw_csv)
    n_dedup = _count(dedup_csv)

    readme = os.path.join(REPO_ROOT, "README.md")
    txt = open(readme, encoding="utf-8").read()

    counts = {}
    for bkey, board in _load_boards().items():
        snapshot_md, top15_md, n_out = _board_blocks(
            bkey, board, n_raw, n_dedup, today)
        tag = bkey.upper()
        txt = _replace_block(txt, f"SNAPSHOT_{tag}", snapshot_md)
        txt = _replace_block(txt, f"TOP15_{tag}", top15_md)
        counts[bkey] = n_out

    # Atomic write: stage to .tmp, then os.replace, so a crash mid-write
    # never leaves the repo with a half-written README.
    tmp = readme + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(txt)
    os.replace(tmp, readme)
    print("README updated: raw=%d dedup=%d out=%s" % (n_raw, n_dedup, counts))


def _replace_block(txt, name, content):
    start = f"<!--{name}_START-->"
    end = f"<!--{name}_END-->"
    s, e = txt.find(start), txt.find(end)
    if s == -1 or e == -1:
        print(f"WARNING: marker {name} not found in README")
        return txt
    return txt[:s + len(start)] + "\n" + content + "\n" + txt[e:]


if __name__ == "__main__":
    ok = fetch_data()
    if not ok:
        print("FETCH FAILED", file=sys.stderr)
        sys.exit(1)
    run("parse_aa.py")
    run("dedup_aa.py")
    run("score_aa.py")
    update_readme()
    print("BUILD OK")
