#!/usr/bin/env python3
"""检测 model_registry.json 的维护问题，输出候选清单。

merge.py 以 registry 为白名单，registry 维护不当会静默丢数据。本脚本补上
「发现」环节，做两类检测：

1. **新模型**（new_models）：源里出现、registry 完全没有收录的模型。
2. **别名漏配**（missing_aliases）：registry 已收录但某源字段为 null，而该
   源里存在「规范化 slug」对应的数据 —— 数据其实有，只是别名没配。

只读不写 registry —— 入选筛选与别名确认是人工判断。候选写入
results/new_model_candidates.json 并打印告警；发现候选不视为失败
（新模型上线是正常事件，不应阻塞榜单刷新）。

关于扫描范围：
- 新模型只扫 LiveBench + DeepSWE（前沿模型评测源，命名规范、几乎无长尾
  噪音）。EQ-Bench / SWE-bench / AA 含大量 open-weights 长尾与旧模型，
  不纳入新模型扫描。
- 别名漏配检测覆盖 aa / eqbench / deepswe / livebench 四个源：这里用
  registry 的 slug 做确定性反向匹配，不存在长尾噪音问题。
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

# AA 源文件在 scripts/ 下（parse_aa.py 产出），其余源在 .cache/
AA_CSV = os.path.join(BASE, "aa_providers.csv")

# 新模型扫描源：{缓存文件名: registry 中对应的别名字段}
NEW_MODEL_SOURCES = {
    "livebench.csv": "livebench",
    "deepswe.csv": "deepswe",
}


def _norm_candidates(slug):
    """slug 的规范化候选（小写 + 点/连字符互换）。

    registry 用点号（qwen3.8-max），AA 用连字符（qwen3-8-max）；
    DeepSWE/EQ-Bench 两者都有。互换覆盖所有情况。
    """
    s = slug.lower()
    return [s, s.replace(".", "-"), s.replace("-", ".")]


def load_registry(registry_path=REGISTRY):
    with open(registry_path, encoding="utf-8") as f:
        return json.load(f)["models"]


def load_whitelists(registry_path=REGISTRY):
    """按源字段分别收集别名 → {源字段: 小写别名集合}。

    各源命名风格不同（LiveBench 带 -high/-max 后缀、DeepSWE 无后缀、
    AA 用连字符），若混成一个集合，A 源的模型名可能被 B 源的别名
    误判为已覆盖，故按源分开匹配。
    """
    models = load_registry(registry_path)
    wl = {key: set() for key in NEW_MODEL_SOURCES.values()}
    for m in models:
        for key in wl:
            v = m.get(key)
            if v is None:
                continue
            for a in (v if isinstance(v, list) else [v]):
                wl[key].add(a.strip().lower())
    return wl


def _read_col(path, col):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [r.get(col, "").strip() for r in csv.DictReader(f)
                if (r.get(col) or "").strip()]


def detect_new_models(whitelists, cache_dir=CACHE):
    """返回 {源文件名: [未被覆盖的模型名]}（去重、排序）。"""
    out = {}
    for fname, key in NEW_MODEL_SOURCES.items():
        path = os.path.join(cache_dir, fname)
        if not os.path.exists(path):
            out[fname] = []
            continue
        missing = sorted({
            m for m in _read_col(path, "model")
            if m.lower() not in whitelists[key]
        })
        out[fname] = missing
    return out


def detect_missing_aliases(registry=None, cache_dir=CACHE, aa_csv=AA_CSV):
    """检测 registry 字段为 null、但源里有规范化 slug 数据的模型。

    返回 {源字段: ["slug -> 源内候选名", ...]}。
    """
    if registry is None:
        registry = load_registry()

    def _names(path, col):
        if not os.path.exists(path):
            return set()
        return {n.lower() for n in _read_col(path, col)}

    src = {
        "aa": _names(aa_csv, "Model Slug"),
        "eqbench": _names(os.path.join(cache_dir, "eqbench.csv"), "model"),
        "deepswe": _names(os.path.join(cache_dir, "deepswe.csv"), "model"),
        "livebench": _names(os.path.join(cache_dir, "livebench.csv"), "model"),
    }

    out = {k: [] for k in src}
    for m in registry:
        slug = m["slug"]
        # 精确匹配源：aa / eqbench / deepswe（规范化 slug 命中）
        for field in ("aa", "eqbench", "deepswe"):
            if m.get(field) is None:
                for c in _norm_candidates(slug):
                    if c in src[field]:
                        out[field].append(f"{slug} -> {c}")
                        break
        # livebench：effort 后缀不固定，用前缀匹配（保守，只提示）
        if m.get("livebench") is None:
            n = slug.lower().replace(".", "-")
            hit = next((x for x in src["livebench"] if x.startswith(n)), None)
            if hit:
                out["livebench"].append(f"{slug} -> {hit}")
    return out


def write_candidates(result, out_path=OUT):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    os.replace(tmp, out_path)
    return out_path


def main():
    registry = load_registry()
    new_models = detect_new_models(load_whitelists())
    missing = detect_missing_aliases(registry)
    result = {"new_models": new_models, "missing_aliases": missing}
    write_candidates(result)

    n_new = sum(len(v) for v in new_models.values())
    n_missing = sum(len(v) for v in missing.values())

    if n_new:
        print(f"!! 发现 {n_new} 个新模型候选（registry 未收录），"
              f"请评估是否补录：")
        for src, names in new_models.items():
            for n in names:
                print(f"    [新模型 {src}] {n}")
    if n_missing:
        print(f"!! 发现 {n_missing} 个「别名漏配」（源里有数据但 registry 字段"
              f"为 null），请补别名：")
        for src, items in missing.items():
            for it in items:
                print(f"    [漏配 {src}] {it}")
    if not n_new and not n_missing:
        print("无候选（新模型与别名漏配均未发现）")
    # 候选出现不视为失败：返回 0 避免阻塞榜单刷新
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
