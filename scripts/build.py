#!/usr/bin/env python3
"""一键构建：抓取 AA leaderboard → 解析 → 去重 → 评分 → 刷新 README。

可在本地运行，也可由 GitHub Actions 调用。
"""
import json
import os
import re
import sys
import csv
import subprocess
import datetime
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE)
HTML = os.path.join(BASE, "aa_providers.html")
URL = "https://artificialanalysis.ai/leaderboards/providers"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")


def fetch_html():
    """抓最新页面，优先 curl，失败回退 urllib。"""
    try:
        r = subprocess.run(
            ["curl", "-sL", "-A", UA, URL, "-o", HTML, "--max-time", "120"],
            check=False,
        )
        if r.returncode == 0 and os.path.getsize(HTML) > 100_000:
            print("fetched via curl, size=", os.path.getsize(HTML))
            return True
    except FileNotFoundError:
        pass
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    with open(HTML, "wb") as f:
        f.write(data)
    print("fetched via urllib, size=", len(data))
    return os.path.getsize(HTML) > 100_000


def run(script):
    subprocess.run([sys.executable, os.path.join(BASE, script)],
                   cwd=BASE, check=True)


def _count(path):
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8-sig", newline="") as f:
        return sum(1 for _ in csv.reader(f)) - 1


def parse_md_table(path):
    """解析 ranking.md 的 Markdown 表格，返回行列表。

    每行 dict: {Rank, Model, Creator, Score, $/1M, Imputed}
    """
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    rows = []
    in_table = False
    for line in lines:
        line = line.strip()
        if line.startswith("| # |") or line.startswith("|#|"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 6:
                rows.append({
                    "Rank": cells[0],
                    "Model": cells[1],
                    "Creator": cells[2],
                    "Weighted Total": cells[3],
                    "Total $/1M": cells[4],
                    "Imputed": cells[-1],
                })
        elif in_table and not line.startswith("|"):
            break
    return rows


def update_readme():
    """从 ranking.md 解析 Top 15，刷新 README。"""
    ranking_md = os.path.join(REPO_ROOT, "results", "ranking.md")
    meta_json = os.path.join(REPO_ROOT, "results", "meta.json")
    val_json = os.path.join(REPO_ROOT, "results", "validation.json")
    raw_csv = os.path.join(BASE, "aa_providers.csv")
    dedup_csv = os.path.join(BASE, "aa_providers_dedup.csv")
    today = datetime.date.today().isoformat()
    n_raw = _count(raw_csv)
    n_dedup = _count(dedup_csv)

    # 从 ranking.md 取数据
    rows = parse_md_table(ranking_md)
    n_out = len(rows)

    # Top 15
    top = rows[:15]
    lines = [
        "| # | Model | Creator | Score | $/1M | Imputed |",
        "|---|---|---|---|---|---|",
    ]
    for r in top:
        imp = (r["Imputed"] or "").strip()
        score_val = r.get("Weighted Total", "")
        cost_val = r.get("Total $/1M", "")
        lines.append("| {} | {} | {} | {} | {} | {} |".format(
            r["Rank"], r["Model"], r["Creator"],
            score_val, cost_val,
            imp or "\u2014",
        ))
    top15_md = "\n".join(lines)

    # 快照行
    snapshot_parts = [
        f"> {today} 抓取"
        f"（{n_raw} 模型\u00d7服务商 \u2192 去重 {n_dedup}"
        f" \u2192 \u226570 分 {n_out} 行）。"
    ]

    if os.path.exists(val_json):
        with open(val_json, encoding="utf-8") as f:
            val = json.load(f)
        val_lines = []
        for m in ["IFBench", "Terminal-Bench Hard", "Terminal-Bench v2.1",
                   "HLE", "GPQA Diamond"]:
            if m in val and val[m].get("mae") is not None:
                v = val[m]
                val_lines.append(
                    f"{m} MAE={v['mae']:.2f}"
                    f" (\u003e10%: {v['pct_over10']}%/{v['n']})"
                )
        if val_lines:
            snapshot_parts.append(
                f"> 填补验证：{'；'.join(val_lines)}"
            )

    snapshot_md = "\n".join(snapshot_parts)

    readme = os.path.join(REPO_ROOT, "README.md")
    txt = open(readme, encoding="utf-8").read()
    txt = _replace_block(txt, "SNAPSHOT", snapshot_md)
    txt = _replace_block(txt, "TOP15", top15_md)
    open(readme, "w", encoding="utf-8").write(txt)
    print("README updated: raw=%d dedup=%d out=%d" % (n_raw, n_dedup, n_out))


def _replace_block(txt, name, content):
    start = f"<!--{name}_START-->"
    end = f"<!--{name}_END-->"
    s, e = txt.find(start), txt.find(end)
    if s == -1 or e == -1:
        print(f"WARNING: marker {name} not found in README")
        return txt
    return txt[:s + len(start)] + "\n" + content + "\n" + txt[e:]


if __name__ == "__main__":
    ok = fetch_html()
    if not ok:
        print("FETCH FAILED", file=sys.stderr)
        sys.exit(1)
    run("parse_aa.py")
    run("dedup_aa.py")
    run("score_aa.py")
    update_readme()
    print("BUILD OK")
