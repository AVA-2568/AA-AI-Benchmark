"""End-to-end test for pipeline.run_pipeline.

Loads the committed fixture (full 396-row dedup, deterministic
order) + the real config.json, runs the shared pipeline into
throwaway dirs, and asserts:

* determinism  — two independent runs produce byte-identical output
* reproducibility — output matches the committed golden snapshot
* structure     — every score >= threshold, validation JSON has all
                 pool-metric keys

This locks the refactored algorithm: any future drift in
imputation / scoring changes the hashes and fails the test.
Does NOT touch production results/.
"""
import csv
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS = os.path.join(_REPO, "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from pipeline import read_rows, run_pipeline, sha256  # noqa: E402


FX = os.path.join(_REPO, "tests", "fixtures")
FIXTURE = os.path.join(FX, "sample_dedup.csv")
GOLDEN_GENERAL = os.path.join(FX, "expected_sample_general.csv")
CONFIG = os.path.join(_REPO, "config.json")


def _cfg():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def _golden_count():
    with open(GOLDEN_GENERAL, encoding="utf-8-sig") as f:
        return sum(1 for _ in csv.DictReader(f))


def _board_metrics(board_cfg):
    """Global-weighted metric names for one leaderboard (what its
    validation JSON keys should match)."""
    ms = []
    for cat in board_cfg["categories"]:
        for m in cat["metrics"]:
            ms.append(m["name"])
    return ms


def test_e2e_deterministic_and_matches_golden(tmp_path):
    cfg = _cfg()
    rows = read_rows(FIXTURE)

    d1 = str(tmp_path / "run1")
    d2 = str(tmp_path / "run2")
    run_pipeline(rows, cfg, d1)
    run_pipeline(rows, cfg, d2)

    g1 = os.path.join(d1, "aa_general_scored.csv")
    g2 = os.path.join(d2, "aa_general_scored.csv")
    # determinism: two runs identical
    assert sha256(g1) == sha256(g2)
    # reproducibility: matches committed golden snapshot
    assert sha256(g1) == sha256(GOLDEN_GENERAL)


def test_e2e_general_structure(tmp_path):
    cfg = _cfg()
    rows = read_rows(FIXTURE)
    out = str(tmp_path / "run")
    run_pipeline(rows, cfg, out)

    g = os.path.join(out, "aa_general_scored.csv")
    with open(g, encoding="utf-8-sig") as f:
        scored = list(csv.DictReader(f))
    # all emitted rows clear the threshold
    assert scored, "no rows scored"
    for r in scored:
        assert float(r["Weighted Total"]) >= cfg["score_threshold"]
    # row count is stable vs golden
    assert len(scored) == _golden_count()

    # validation JSON covers this board's own global metrics
    with open(os.path.join(out, "validation_general.json"), encoding="utf-8") as f:
        val = json.load(f)
    assert set(val.keys()) == set(_board_metrics(cfg["leaderboards"]["general"]))


def test_e2e_text_structure(tmp_path):
    cfg = _cfg()
    rows = read_rows(FIXTURE)
    out = str(tmp_path / "run")
    run_pipeline(rows, cfg, out)

    t = os.path.join(out, "aa_text_scored.csv")
    with open(t, encoding="utf-8-sig") as f:
        scored = list(csv.DictReader(f))
    assert scored, "no text rows scored"
    for r in scored:
        assert float(r["Weighted Total"]) >= cfg["score_threshold"]

    with open(os.path.join(out, "validation_text.json"), encoding="utf-8") as f:
        val = json.load(f)
    assert set(val.keys()) == set(_board_metrics(cfg["leaderboards"]["text"]))
