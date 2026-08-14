#!/usr/bin/env python3
"""检测各源中未被 model_registry.json 覆盖的新模型，输出候选清单。

背景：merge.py 以 model_registry.json 为白名单，只输出注册表里已有的模型，
源里出现的新模型会被静默丢弃。本脚本补上「发现」这一环——对比各源模型名与
registry 对应源的别名，找出未被覆盖的候选，提醒维护者评估补录。

只扫「第一梯队评测源」LiveBench 与 DeepSWE：这两个源只测当前主流模型、
命名规范、几乎无长尾噪音，是新模型发布后最快收录的第一梯队雷达。
EQ-Bench / SWE-bench / AA 因含大量 open-weights 长尾、旧模型与重复变体
（实测未覆盖率分别约 79% / 97% / 34%），不纳入自动扫描。

不自动修改 registry —— 第一梯队筛选与别名确认是人工判断。脚本只负责发现，
候选写入 results/new_model_candidates.json 并打印告警；发现候选不视为失败
（新模型上线是正常事件，不应阻塞榜单刷新）。
"""
import csv
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE)
REGISTRY = os.path.join(BASE, "model_registry.json")
CACHE = os.path.join(BASE, ".cache")
RESULTS = os.path.join(REPO_ROOT, "results")
OUT = os.path.join(RESULTS, "new_model_candidates.json")

# 主扫描源：{缓存文件名: registry 中对应的别名字段}
SOURCES = {
    "livebench.csv": "livebench",
    "deepswe.csv": "deepswe",
}


def load_whitelists(registry_path=REGISTRY):
    """按源字段分别收集别名 → {源字段: 小写别名集合}。

    各源命名风格不同（LiveBench 带 -high/-max 后缀、DeepSWE 无后缀、
    AA 用连字符），若混成一个集合，A 源的模型名可能被 B 源的别名
    误判为已覆盖，故按源分开匹配。
    """
    with open(registry_path, encoding="utf-8") as f:
        models = json.load(f)["models"]
    wl = {key: set() for key in SOURCES.values()}
    for m in models:
        for key in wl:
            v = m.get(key)
            if v is None:
                continue
            for a in (v if isinstance(v, list) else [v]):
                wl[key].add(a.strip().lower())
    return wl


def _read_model_col(path):
    """读 CSV 的 model 列，返回非空模型名列表。"""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [r.get("model", "").strip() for r in csv.DictReader(f)
                if (r.get("model") or "").strip()]


def detect_candidates(whitelists, cache_dir=CACHE):
    """返回 {源文件名: [未被覆盖的模型名]}（去重、排序）。"""
    out = {}
    for fname, key in SOURCES.items():
        path = os.path.join(cache_dir, fname)
        if not os.path.exists(path):
            out[fname] = []
            continue
        missing = sorted({
            m for m in _read_model_col(path)
            if m.lower() not in whitelists[key]
        })
        out[fname] = missing
    return out


def write_candidates(candidates, out_path=OUT):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    os.replace(tmp, out_path)
    return out_path


def main():
    whitelists = load_whitelists()
    candidates = detect_candidates(whitelists)
    write_candidates(candidates)
    total = sum(len(v) for v in candidates.values())
    if total:
        print(f"!! 发现 {total} 个未被 registry 覆盖的模型候选，"
              f"请评估是否补录 model_registry.json：")
        for src, names in candidates.items():
            for n in names:
                print(f"    [{src}] {n}")
    else:
        print("无新模型候选（LiveBench/DeepSWE 已全部被 registry 覆盖）")
    # 新模型出现不视为失败：返回 0 避免阻塞榜单刷新
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
