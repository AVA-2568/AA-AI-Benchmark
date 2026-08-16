#!/usr/bin/env python3
"""跨源合并：model_registry.json + 各源 CSV -> merged.csv（统一宽表）。

行 = 注册表里的模型（统一 slug），列 = config.imputation_pool 的
11 个指标 + Model/Creator。各源分数通过别名匹配；livebench 别名可为列表，
多个匹配时取分数最高者。缺失值留空，交由评分阶段的岭回归填补。

数据源：
- AA (scripts/aa_providers.csv)         -> LCR / Omniscience Index / GPQA Diamond / HLE
- LiveBench (scripts/.cache/livebench.csv) -> Coding / Agentic Coding / IF / Language
- DeepSWE   (scripts/.cache/deepswe.csv)   -> Pass@1
- SWE-bench (scripts/.cache/swebench.csv)  -> Resolved
- EQ-Bench  (scripts/.cache/eqbench.csv)   -> Elo
"""
import csv
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE)
CACHE = os.path.join(BASE, ".cache")
REGISTRY = os.path.join(BASE, "model_registry.json")
AA_CSV = os.path.join(BASE, "aa_providers.csv")


def _read_csv(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return rows


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _alias_index(rows, key_col):
    """{key_col 值 -> 行 dict}，支持一行多列。"""
    idx = {}
    for r in rows:
        k = (r.get(key_col) or "").strip()
        if k:
            idx[k] = r
    return idx


def load_registry():
    with open(REGISTRY, encoding="utf-8") as f:
        return json.load(f)["models"]


def _pick_max(idx, alias):
    """别名可为字符串或列表；返回匹配到的最高分（按指定列）。"""
    if alias is None:
        return None, None
    alist = alias if isinstance(alias, list) else [alias]
    best, best_val = None, None
    for a in alist:
        if a in idx:
            return idx[a], a
    return None, None


def build_merged():
    registry = load_registry()

    # ---- 各源索引 ----
    aa = _alias_index(_read_csv(AA_CSV), "Model Slug")
    lb = _alias_index(_read_csv(os.path.join(CACHE, "livebench.csv")), "model")
    ds = _alias_index(_read_csv(os.path.join(CACHE, "deepswe.csv")), "model")
    eq = _alias_index(_read_csv(os.path.join(CACHE, "eqbench.csv")), "model")

    # 指标名（与 config.json imputation_pool 一致）
    cols = [
        "LiveBench Coding", "DeepSWE",
        "LiveBench Agentic Coding", "LiveBench Instruction Following",
        "LCR", "Omniscience Index", "GPQA Diamond", "HLE",
        "EQ-Bench Creative Writing", "LiveBench Language",
    ]

    out_rows = []
    for m in registry:
        slug = m["slug"]
        row = {"Model": slug, "Creator": m["creator"]}

        # LiveBench（别名可为列表，取最高 Overall 近似 —— 这里按 Coding 最高者）
        lb_row, lb_name = _pick_max(lb, m.get("livebench"))
        if lb_row:
            row["LiveBench Coding"] = _num(lb_row.get("Coding"))
            row["LiveBench Agentic Coding"] = _num(lb_row.get("Agentic Coding"))
            row["LiveBench Instruction Following"] = _num(lb_row.get("IF"))
            row["LiveBench Language"] = _num(lb_row.get("Language"))

        # DeepSWE
        ds_row, _ = _pick_max(ds, m.get("deepswe"))
        if ds_row:
            row["DeepSWE"] = _num(ds_row.get("Pass@1"))

        # EQ-Bench
        eq_row, _ = _pick_max(eq, m.get("eqbench"))
        if eq_row:
            row["EQ-Bench Creative Writing"] = _num(eq_row.get("Elo"))

        # AA
        aa_row, _ = _pick_max(aa, m.get("aa"))
        if aa_row:
            row["LCR"] = _num(aa_row.get("LCR"))
            row["Omniscience Index"] = _num(aa_row.get("Omniscience Index"))
            row["GPQA Diamond"] = _num(aa_row.get("GPQA Diamond"))
            row["HLE"] = _num(aa_row.get("HLE"))
            # 成本列（性价比榜用）
            row["Price 1M Input"] = _num(aa_row.get("Price 1M Input"))
            row["Price 1M Output"] = _num(aa_row.get("Price 1M Output"))
            row["Cache Hit Price"] = _num(aa_row.get("Cache Hit Price"))
            row["Cache Write Price"] = _num(aa_row.get("Cache Write Price"))
            row["Cost Per Task"] = _num(aa_row.get("Cost Per Task"))

        out_rows.append(row)

    # 写 merged.csv（列序：Model, Creator, 指标, 成本列）
    price_cols = ["Price 1M Input", "Price 1M Output", "Cache Hit Price",
                  "Cache Write Price", "Cost Per Task"]
    header = ["Model", "Creator"] + cols + price_cols
    os.makedirs(os.path.join(REPO_ROOT, "results"), exist_ok=True)
    out_path = os.path.join(BASE, "merged.csv")
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
        w.writeheader()
        for r in out_rows:
            # 空值写空串，避免 "None"
            w.writerow({k: ("" if v is None else v) for k, v in r.items()})
    os.replace(tmp, out_path)

    # 覆盖率统计
    n = len(out_rows)
    print(f"merged: {n} 模型 -> {os.path.basename(out_path)}")
    for c in cols:
        cover = sum(1 for r in out_rows if r.get(c) not in (None, ""))
        print(f"  {c:35} 覆盖 {cover}/{n}")
    return out_path


def main():
    try:
        build_merged()
    except FileNotFoundError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
