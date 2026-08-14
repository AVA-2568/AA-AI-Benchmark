"""Unit tests for detect_new_models (new-model discovery, no network)."""
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


def test_load_whitelists_split_by_source(tmp_path):
    reg = tmp_path / "reg.json"
    _write_registry(str(reg), [
        {"slug": "a", "aa": "a-1", "livebench": ["a-high", "a"],
         "deepswe": None, "swebench": None, "eqbench": "a"},
    ])
    wl = dnm.load_whitelists(str(reg))
    # livebench 别名单独成集，不含 eqbench/aa 的别名
    assert wl["livebench"] == {"a-high", "a"}
    assert wl["deepswe"] == set()


def test_detect_flags_only_uncovered(tmp_path):
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

    wl = dnm.load_whitelists(str(reg))
    got = dnm.detect_candidates(wl, cache_dir=str(cache))
    assert got["livebench.csv"] == ["some-new-model-high"]
    assert got["deepswe.csv"] == ["another-new-model"]


def test_detect_no_cross_source_confusion(tmp_path):
    """livebench 源里的名字只匹配 livebench 别名，不被 eqbench 别名误判覆盖。"""
    reg = tmp_path / "reg.json"
    _write_registry(str(reg), [
        {"slug": "x", "aa": None, "livebench": "x-high", "deepswe": None,
         "swebench": None, "eqbench": "x"},
    ])
    cache = tmp_path / "cache"
    cache.mkdir()
    # livebench 里出现 "x"（无 -high 后缀），它不是 x 的 livebench 别名
    _write_cache(str(cache), "livebench.csv", ["x"])
    _write_cache(str(cache), "deepswe.csv", [])

    wl = dnm.load_whitelists(str(reg))
    got = dnm.detect_candidates(wl, cache_dir=str(cache))
    # 若按全集匹配会误判为已覆盖；按源匹配应报出 "x"
    assert got["livebench.csv"] == ["x"]


def test_detect_case_insensitive(tmp_path):
    reg = tmp_path / "reg.json"
    _write_registry(str(reg), [
        {"slug": "x", "aa": None, "livebench": "X-High", "deepswe": None,
         "swebench": None, "eqbench": None},
    ])
    cache = tmp_path / "cache"
    cache.mkdir()
    _write_cache(str(cache), "livebench.csv", ["x-high"])
    _write_cache(str(cache), "deepswe.csv", [])

    wl = dnm.load_whitelists(str(reg))
    got = dnm.detect_candidates(wl, cache_dir=str(cache))
    assert got["livebench.csv"] == []  # x-high 命中 X-High（大小写不敏感）


def test_detect_missing_cache(tmp_path):
    reg = tmp_path / "reg.json"
    _write_registry(str(reg), [])
    wl = dnm.load_whitelists(str(reg))
    got = dnm.detect_candidates(wl, cache_dir=str(tmp_path / "nope"))
    assert got == {"livebench.csv": [], "deepswe.csv": []}
