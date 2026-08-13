"""Unit tests for pipeline.scoring (norm / fmt_val / score_board).

``score_board`` is tested in isolation with a lightweight fake
engine (mimics the attributes the real ``ImputationEngine``
exposes) so the test does not depend on imputation numerics.
"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS = os.path.join(_REPO, "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from pipeline import fmt_val, norm, score_board  # noqa: E402


# ---- norm ----

def test_norm_midpoint():
    assert norm(50, 0, 100) == 50.0

def test_norm_bounds():
    assert norm(0, 0, 100) == 0.0
    assert norm(100, 0, 100) == 100.0

def test_norm_flat_range():
    assert norm(7, 3, 3) == 50.0


# ---- fmt_val ----

def test_fmt_val_plain():
    assert fmt_val(0.531, False, False) == "0.531"

def test_fmt_val_imputed():
    assert fmt_val(0.531, True, False) == "0.531*"

def test_fmt_val_low_beats_imputed():
    assert fmt_val(0.531, True, True) == "0.531**"


# ---- score_board (isolated fake engine) ----

class FakeEngine:
    """Minimal stand-in for ImputationEngine for score_board."""

    def __init__(self):
        self.pool = ["m1", "m2"]
        # (lo, hi, top50mean, p90, clip)
        self.stats = {
            "m1": (0.0, 100.0, 50.0, 95.0, 100.0),
            "m2": (0.0, 50.0, 25.0, 47.0, 50.0),
        }
        self.cur = {"m1": [80.0, 20.0], "m2": [40.0, 10.0]}
        self.raw = {"m1": [80.0, 20.0], "m2": [40.0, 10.0]}
        self.imputation_quality = {
            "m1": {"n_train": 2},
            "m2": {"n_train": 2},
        }
        self.min_samples = 3


_BOARD = {
    "categories": [
        {"name": "c1", "weight": 0.5,
         "metrics": [{"name": "m1", "sub_weight": 1.0}]},
        {"name": "c2", "weight": 0.5,
         "metrics": [{"name": "m2", "sub_weight": 1.0}]},
    ]
}

_COST = {"input_share": 0.7, "output_share": 0.3, "cache_hit_rate": 0.5}

_ROWS = [
    {"Model": "A", "Price 1M Input": "1.0",
     "Price 1M Output": "2.0", "Cache Hit Price": "0.1"},
    {"Model": "B", "Price 1M Input": "1.0",
     "Price 1M Output": "2.0", "Cache Hit Price": "0.1"},
]


def test_score_board_sorts_and_ranks():
    out, headers = score_board(_ROWS, _BOARD, FakeEngine(),
                                 _COST, 0.1, 0.0)
    assert len(out) == 2
    # both models: m1 norm=80, m2 norm=80 -> total=80; tie -> Model order
    assert out[0]["Model"] == "A"
    assert out[0]["Rank"] == 1
    assert out[1]["Model"] == "B"
    assert out[1]["Rank"] == 2
    assert out[0]["Weighted Total"] == 80.0


def test_score_board_threshold_filter():
    out, _ = score_board(_ROWS, _BOARD, FakeEngine(), _COST, 0.1, 90.0)
    assert out == []  # totals are 80 < 90


def test_score_board_headers_and_norm_columns():
    _, headers = score_board(_ROWS, _BOARD, FakeEngine(), _COST, 0.1, 0.0)
    assert "Rank" in headers and "Model" in headers
    assert "Weighted Total" in headers
    assert "m1" in headers and "m1 (norm)" in headers


def test_score_board_imputed_marker():
    eng = FakeEngine()
    # force one cell to be imputed AND below min_samples -> "(low)" marker
    eng.raw = {"m1": [80.0, None], "m2": [40.0, 10.0]}
    eng.cur = {"m1": [80.0, 33.0], "m2": [40.0, 10.0]}
    eng.imputation_quality = {"m1": {"n_train": 1}, "m2": {"n_train": 2}}
    rows = [
        {"Model": "A", "Price 1M Input": "1.0",
         "Price 1M Output": "2.0", "Cache Hit Price": "0.1"},
        {"Model": "B", "Price 1M Input": "1.0",
         "Price 1M Output": "2.0", "Cache Hit Price": "0.1"},
    ]
    out, _ = score_board(rows, _BOARD, eng, _COST, 0.1, 0.0)
    b = next(r for r in out if r["Model"] == "B")
    # imputed AND below min_samples -> "(reg,low)" marker in Imputed column
    assert "m1(reg,low)" in b["Imputed"]


# ---- cost is unit-price only (thinking effort NOT a factor) ----

def test_score_board_cost_independent_of_thinking_effort():
    """Total $/1M is a per-token unit price: it must depend only on the
    provider's list prices, never on reasoning flag or thinking level.
    Same price -> same $/1M, no matter the (max)/(high) suffix."""
    eng = FakeEngine()
    eng.raw = {"m1": [80.0, 20.0, 20.0], "m2": [40.0, 10.0, 10.0]}
    eng.cur = dict(eng.raw)
    rows = [
        {"Model": "R (max)", "Reasoning Model": "True",
         "Price 1M Input": "5.0", "Price 1M Output": "25.0",
         "Cache Hit Price": "0.5"},
        {"Model": "R (high)", "Reasoning Model": "True",
         "Price 1M Input": "5.0", "Price 1M Output": "25.0",
         "Cache Hit Price": "0.5"},
        {"Model": "N", "Reasoning Model": "False",
         "Price 1M Input": "5.0", "Price 1M Output": "25.0",
         "Cache Hit Price": "0.5"},
    ]
    out, headers = score_board(rows, _BOARD, eng, _COST, 0.1, 0.0)
    by_model = {r["Model"]: r for r in out}
    costs = {float(by_model[m]["Total $/1M"]) for m in by_model}
    assert len(costs) == 1, "same list price must yield identical $/1M"
    assert "Reasoning Cost ×" not in headers

