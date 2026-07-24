#!/usr/bin/env python3
"""一键构建：抓取 AA leaderboard → 解析 → 去重 → 评分 → 导出 → 刷新 README。

可在本地运行，也可由 GitHub Actions 调用（路径无关，仅依赖仓库根目录）。
"""
import os
import sys
import csv
import subprocess
import datetime
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(BASE, "aa_providers.html")
URL = "https://artificialanalysis.ai/leaderboards/providers"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def fetch_html():
    """抓最新页面，优先 curl，失败回退 urllib。返回是否成功。"""
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
    # 回退：urllib
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    with open(HTML, "wb") as f:
        f.write(data)
    print("fetched via urllib, size=", len(data))
    return os.path.getsize(HTML) > 100_000


def run(script):
    """运行仓库内的步骤脚本。"""
    subprocess.run([sys.executable, os.path.join(BASE, script)],
                   cwd=BASE, check=True)


def _count(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return sum(1 for _ in csv.reader(f)) - 1


def update_readme():
    """用最新 scored.csv 刷新 README 的快照行与 Top15 表。"""
    scored = os.path.join(BASE, "aa_providers_scored.csv")
    raw = os.path.join(BASE, "aa_providers.csv")
    dedup = os.path.join(BASE, "aa_providers_dedup.csv")
    today = datetime.date.today().isoformat()
    n_raw = _count(raw)
    n_dedup = _count(dedup)
    n_out = _count(scored)

    with open(scored, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    top = rows[:15]
    lines = [
        f"| # | 模型 | 厂商 | 总分 | $/1M | 回归填补项 |",
        "|---|---|---|---|---|---|",
    ]
    for r in top:
        imp = (r["Imputed"] or "").strip()
        lines.append("| {} | {} | {} | {} | {} | {} |".format(
            r["Rank"], r["Model"], r["Creator"],
            r["Weighted Total"], r["Total $/1M"],
            imp or "—",
        ))
    top15_md = "\n".join(lines)

    snapshot_md = (f"> 数据快照：{today} 抓取（{n_raw} 模型×服务商 → "
                   f"去重 {n_dedup} → 取前 15% = {n_out} 行）。")

    readme = os.path.join(BASE, "README.md")
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
    run("export_deliverables.py")
    update_readme()
    print("BUILD OK")
