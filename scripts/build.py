#!/usr/bin/env python3
"""一键构建：抓取 AA leaderboard -> 解析 -> 去重 -> 评分 -> 刷新 README。

抓取策略（与 parse_aa.py 的三级解析链配套）：
1. 主路径：带 ``RSC: 1`` 头请求同一 URL，拿 RSC 数据流（~2.4MB 纯数据）
2. 回退：抓整页 HTML（~5.4MB），parse_aa.py 走 __next_f.push / __NEXT_DATA__
3. 最后手段：沿用上次运行留下的缓存文件并打警告（CI 日志可见）

可在本地运行，也可由 GitHub Actions 调用。
"""
import argparse
import datetime
import csv
import hashlib
import json
import os
import subprocess
import sys
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
MANIFEST = os.path.join(REPO_ROOT, "results", "manifest.json")


class BuildError(RuntimeError):
    """Raised when a build cannot produce a trustworthy result."""


class StaleCacheError(BuildError):
    """Raised when only stale input is available without explicit opt-in."""


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
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, out_path)
            print(f"fetched via urllib -> {os.path.basename(out_path)}, "
                  f"size={len(data)}")
            return True
    except Exception as e:
        print(f"urllib fetch failed: {e}")
    if os.path.exists(tmp):
        os.remove(tmp)
    return False


def fetch_data(allow_stale=False, offline=False):
    """获取 RSC/HTML；缓存只有显式允许时才能作为输入。"""
    if offline:
        if os.path.exists(RSC) or os.path.exists(HTML):
            print("offline mode: using existing cache")
            return True, True
        raise BuildError("offline mode requested but no input cache exists")
    if _fetch(URL, RSC, RSC_MIN_SIZE, {"RSC": "1"}):
        return True, False
    print("!! RSC fetch failed, falling back to full HTML")
    if _fetch(URL, HTML, HTML_MIN_SIZE):
        # HTML 是新鲜的，删掉过期 RSC，防止 parse_aa.py 优先吃到旧数据
        if os.path.exists(RSC):
            os.remove(RSC)
            print("removed stale aa_providers.rsc (fresh HTML takes over)")
        return True, False
    if allow_stale and (os.path.exists(RSC) or os.path.exists(HTML)):
        print("!! WARNING: both fetches failed, explicitly reusing STALE cache")
        return True, True
    if os.path.exists(RSC) or os.path.exists(HTML):
        raise StaleCacheError(
            "both fetches failed; stale cache exists but --allow-stale was not set"
        )
    return False, False


def run(script):
    subprocess.run([sys.executable, os.path.join(BASE, script)],
                   cwd=BASE, check=True)


def _count(path):
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8-sig", newline="") as f:
        return sum(1 for _ in csv.reader(f)) - 1


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_config():
    with open(os.path.join(REPO_ROOT, "config.json"), encoding="utf-8") as f:
        return json.load(f)


def _load_boards():
    return _load_config()["leaderboards"]


def _board_blocks(bkey, board, n_models, today):
    """生成单个榜单的 (snapshot_md, top15_md)。"""
    scored = os.path.join(REPO_ROOT, "results", board["output_csv"])
    val_json = os.path.join(REPO_ROOT, "results", board["validation_json"])
    n_out = _count(scored)

    with open(scored, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    top = rows[:15]
    if board.get("rank_by") == "value":
        # 性价比榜：展示真实成本（订阅+缓存）与性价比分
        lines = [
            "| # | Model | Creator | Score | $/1M | Effective $/1M | Value | Imputed |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for r in top:
            imp = (r["Imputed"] or "").strip()
            lines.append("| {} | {} | {} | {} | {} | {} | {} | {} |".format(
                r["Rank"], r["Model"], r["Creator"],
                r.get("Weighted Total") or "",
                r.get("Total $/1M") or "",
                r.get("Effective $/1M") or "",
                r.get("Value Score") or "",
                imp or "-",
            ))
    else:
        lines = [
            "| # | Model | Creator | Score | Imputed |",
            "|---|---|---|---|---|",
        ]
        for r in top:
            imp = (r["Imputed"] or "").strip()
            lines.append("| {} | {} | {} | {} | {} |".format(
                r["Rank"], r["Model"], r["Creator"],
                r.get("Weighted Total") or "",
                imp or "-",
            ))
    top15_md = "\n".join(lines)

    snapshot_parts = [
        f"> {today} 抓取（{n_models} 第一梯队模型 -> {n_out} 行）。"
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
    merged_csv = os.path.join(BASE, "merged.csv")
    today = datetime.date.today().isoformat()
    n_models = _count(merged_csv)

    readme = os.path.join(REPO_ROOT, "README.md")
    txt = open(readme, encoding="utf-8").read()

    counts = {}
    for bkey, board in _load_boards().items():
        snapshot_md, top15_md, n_out = _board_blocks(
            bkey, board, n_models, today)
        tag = bkey.upper()
        snapshot_name = f"SNAPSHOT_{tag}"
        top15_name = f"TOP15_{tag}"
        if not _has_markers(txt, snapshot_name) or not _has_markers(txt, top15_name):
            raise BuildError(f"README marker missing for {bkey}")
        txt = _replace_block(txt, snapshot_name, snapshot_md)
        txt = _replace_block(txt, top15_name, top15_md)
        counts[bkey] = n_out

    # Atomic write: stage to .tmp, then os.replace, so a crash mid-write
    # never leaves the repo with a half-written README.
    tmp = readme + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(txt)
    os.replace(tmp, readme)
    print("README updated: models=%d out=%s" % (n_models, counts))


def _has_markers(txt, name):
    start = f"<!--{name}_START-->"
    end = f"<!--{name}_END-->"
    s, e = txt.find(start), txt.find(end)
    return s != -1 and e != -1 and e >= s


def _replace_block(txt, name, content):
    """Replace a README marker block; return original text if absent."""
    start = f"<!--{name}_START-->"
    end = f"<!--{name}_END-->"
    s, e = txt.find(start), txt.find(end)
    if s == -1 or e == -1 or e < s:
        print(f"ERROR: marker {name} not found in README", file=sys.stderr)
        return txt
    return txt[:s + len(start)] + "\n" + content + "\n" + txt[e:]


def _read_last_parser():
    """Read the parser name recorded by parse_aa.py (best-effort)."""
    path = os.path.join(BASE, ".last_parser")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return fh.read().strip() or None


def _write_manifest(stale, parser=None):
    config_path = os.path.join(REPO_ROOT, "config.json")
    merged_csv = os.path.join(BASE, "merged.csv")
    manifest = {
        "run_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source_url": URL,
        "parser": parser,
        "input_sha256": _sha256(merged_csv) if os.path.exists(merged_csv) else None,
        "config_sha256": _sha256(config_path),
        "algorithm_version": "0a62096",
        "models": _count(merged_csv),
        "stale": stale,
    }
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    tmp = MANIFEST + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, MANIFEST)
    print(f"manifest updated -> {MANIFEST}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true",
                        help="use existing input cache without network")
    parser.add_argument("--allow-stale", action="store_true",
                        help="allow stale cache when both fetches fail")
    args = parser.parse_args(argv)
    try:
        ok, stale = fetch_data(allow_stale=args.allow_stale, offline=args.offline)
        if not ok:
            raise BuildError("fetch failed")
        run("parse_aa.py")
        if args.offline:
            print("offline mode: skipping independent-source fetch (using cache)")
        else:
            run("fetch_sources.py")
        run("merge.py")
        run("score_aa.py")
        if stale:
            print("stale input: skipping README update")
        else:
            update_readme()
        _write_manifest(stale=stale, parser=_read_last_parser())
    except (BuildError, subprocess.CalledProcessError) as exc:
        print(f"BUILD FAILED: {exc}", file=sys.stderr)
        return 1
    print("BUILD OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
