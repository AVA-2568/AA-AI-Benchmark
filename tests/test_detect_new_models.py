"""Unit tests for detect_new_models (new-model + alias-missing discovery)."""
import csv
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS = os.path.join(_REPO, "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

import detect_new_models as dnm  # noqa: E402


def _write_registry(path, models):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"models": models}, f)


def _write_cache(cache_dir, fname, models):
    p = os.path.join(cache_dir, fname)
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "score"])
        for m in models:
            w.writerow([m, "1.0"])


def _write_aa(path, slugs):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Model Slug", "LCR"])
        for s in slugs:
            w.writerow([s, "0.5"])


# ---- load_whitelists ----

def test_load_whitelists_split_by_source(tmp_path):
    reg = tmp_path / "reg.json"
    _write_registry(str(reg), [
        {"slug": "a", "aa": "a-1", "livebench": ["a-high", "a"],
         "deepswe": None, "swebench": None, "eqbench": "a"},
    ])
    wl = dnm.load_whitelists(str(reg))
    assert wl["livebench"] == {"a-high", "a"}
    assert wl["deepswe"] == set()


# ---- detect_new_models ----

def test_new_models_flags_only_uncovered(tmp_path):
    reg = tmp_path / "reg.json"
    _write_registry(str(reg), [
        {"slug": "gemini-3.7-flash", "aa": "gemini-3-7-flash",
         "livebench": "gemini-3.7-flash-high", "deepswe": "gemini-3.7-flash",
         "swebench": None, "eqbench": "gemini-3.7-flash"},
    ])
    cache = tmp_path / "cache"
    cache.mkdir()
    _write_cache(str(cache), "livebench.csv",
                 ["gemini-3.7-flash-high", "some-new-model-high"])
    _write_cache(str(cache), "deepswe.csv",
                 ["gemini-3.7-flash", "another-new-model"])

    got = dnm.detect_new_models(dnm.load_whitelists(str(reg)),
                                cache_dir=str(cache))
    assert got["livebench.csv"] == ["some-new-model-high"]
    assert got["deepswe.csv"] == ["another-new-model"]


def test_new_models_no_cross_source_confusion(tmp_path):
    """livebench 源里的名字只匹配 livebench 别名，不被 eqbench 别名误判覆盖。"""
    reg = tmp_path / "reg.json"
    _write_registry(str(reg), [
        {"slug": "x", "aa": None, "livebench": "x-high", "deepswe": None,
         "swebench": None, "eqbench": "x"},
    ])
    cache = tmp_path / "cache"
    cache.mkdir()
    _write_cache(str(cache), "livebench.csv", ["x"])
    _write_cache(str(cache), "deepswe.csv", [])

    got = dnm.detect_new_models(dnm.load_whitelists(str(reg)),
                                cache_dir=str(cache))
    assert got["livebench.csv"] == ["x"]


def test_new_models_case_insensitive(tmp_path):
    reg = tmp_path / "reg.json"
    _write_registry(str(reg), [
        {"slug": "x", "aa": None, "livebench": "X-High", "deepswe": None,
         "swebench": None, "eqbench": None},
    ])
    cache = tmp_path / "cache"
    cache.mkdir()
    _write_cache(str(cache), "livebench.csv", ["x-high"])
    _write_cache(str(cache), "deepswe.csv", [])

    got = dnm.detect_new_models(dnm.load_whitelists(str(reg)),
                                cache_dir=str(cache))
    assert got["livebench.csv"] == []


def test_new_models_missing_cache(tmp_path):
    reg = tmp_path / "reg.json"
    _write_registry(str(reg), [])
    got = dnm.detect_new_models(dnm.load_whitelists(str(reg)),
                                cache_dir=str(tmp_path / "nope"))
    assert got == {"livebench.csv": [], "deepswe.csv": []}


# ---- detect_missing_aliases ----

def test_missing_aliases_aa_detected(tmp_path):
    """registry aa=null 但 AA 源有连字符 slug → 报漏配。"""
    reg = [
        {"slug": "qwen3.8-max", "aa": None, "livebench": "qwen3.8-max",
         "deepswe": "qwen3.8-max", "swebench": None, "eqbench": None},
    ]
    aa = tmp_path / "aa.csv"
    _write_aa(str(aa), ["qwen3-8-max"])

    got = dnm.detect_missing_aliases(reg, cache_dir=str(tmp_path / "nope"),
                                     aa_csv=str(aa))
    assert got["aa"] == ["qwen3.8-max -> qwen3-8-max"]


def test_missing_aliases_no_false_positive(tmp_path):
    """字段已配（值在源里）→ 不报漏配；字段 null 但源里也没有 → 不报。"""
    reg = [
        {"slug": "a", "aa": "a-1", "livebench": None, "deepswe": None,
         "swebench": None, "eqbench": None},
        {"slug": "b", "aa": None, "livebench": None, "deepswe": None,
         "swebench": None, "eqbench": None},
    ]
    aa = tmp_path / "aa.csv"
    _write_aa(str(aa), ["a-1"])  # 只有 a，没有 b

    got = dnm.detect_missing_aliases(reg, cache_dir=str(tmp_path / "nope"),
                                     aa_csv=str(aa))
    assert got["aa"] == []  # a 已配、b 源里没有 → 都不报
