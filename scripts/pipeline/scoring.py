"""Scoring: min-max norm, weighted total, cost, ranking + threshold."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from .config import board_weights, to_float
from .models import ScoredModel


def norm(v, lo, hi):
    """Min-max normalize v into 0-100 using [lo, hi]. Flat range -> 50."""
    if hi == lo:
        return 50.0
    return (v - lo) / (hi - lo) * 100.0


def fmt_val(val, is_imputed, is_low):
    s = str(round(val, 3))
    if is_low:
        return s + "**"
    if is_imputed:
        return s + "*"
    return s


_THINKING_LEVEL_RE = re.compile(
    r"\((max|xhigh|high|medium|low|minimal)\)", re.IGNORECASE)


def resolve_reasoning_multiplier(row, cost):
    """Effective output-term multiplier from reasoning effort.

    Reasoning tokens are billed as *output* tokens, so a thinking
    model's real $/1M is materially higher than a non-reasoning model
    with the same list price. We model that as a multiplier K on the
    output cost term:

    - non-reasoning (flag False, or name carries "non-reasoning" /
      "no reasoning")           -> K = 1.0
    - reasoning, recognized level (max/high/...) -> thinking_multipliers[lvl]
    - reasoning, no recognized level          -> reasoning_output_multiplier

    This makes the estimated cost vary with thinking effort instead of
    being identical across reasoning vs non-reasoning variants.
    """
    base = float(cost.get("reasoning_output_multiplier", 1.0) or 1.0)
    lvl_map = cost.get("thinking_multipliers") or {}

    model = (row.get("Model") or "")
    mlow = model.lower()
    flag = str(row.get("Reasoning Model") or "").strip().lower()

    is_reasoning = flag in ("true", "yes", "1", "y")
    # explicit non-reasoning marker overrides a stray boolean
    if "non-reasoning" in mlow or "no reasoning" in mlow:
        is_reasoning = False

    if not is_reasoning:
        return 1.0

    m = _THINKING_LEVEL_RE.search(model)
    lvl = m.group(1).lower() if m else None
    if lvl and lvl in lvl_map:
        return float(lvl_map[lvl])
    return base


def score_board(rows, board, engine, cost, cache_multiplier, score_threshold):
    """Score one leaderboard. Returns (scored_rows, n_out).

    ``engine`` provides stats / cur / raw / imputation_quality and
    the shared pool. No algorithm is duplicated here.
    """
    cats, glob = board_weights(board)
    metrics = list(glob.keys())
    pool = engine.pool
    stats = engine.stats
    cur = engine.cur
    raw = engine.raw
    imp_q = engine.imputation_quality

    input_share = cost["input_share"]
    output_share = cost["output_share"]
    cache_share = cost["cache_hit_rate"]
    min_samples = engine.min_samples

    out = []
    for i, r in enumerate(rows):
        eff = {}
        imputed = []
        for m in metrics:
            if raw[m][i] is not None:
                eff[m] = raw[m][i]
            else:
                n_train = imp_q[m]["n_train"]
                eff[m] = cur[m][i]
                if n_train < min_samples:
                    imputed.append(m + "(low)")
                else:
                    imputed.append(m)
        nrm = {m: norm(eff[m], stats[m][0], stats[m][1]) for m in metrics}
        total = sum(glob[m] * nrm[m] for m in metrics)

        pin = to_float(r.get("Price 1M Input"))
        pout = to_float(r.get("Price 1M Output"))
        pcache = to_float(r.get("Cache Hit Price"))
        # Industry standard: cached tokens ~10% of input price.
        pcache_eff = pcache if pcache is not None else (
            pin * cache_multiplier if pin is not None else None)
        if None in (pin, pout):
            cost_total = None
        else:
            k = resolve_reasoning_multiplier(r, cost)
            cost_in = input_share * (1 - cache_share) * pin
            cost_cache = input_share * cache_share * pcache_eff
            # reasoning tokens are output-priced; scale the output term
            # by the thinking-effort multiplier so cost reflects thinking
            cost_out = output_share * pout * k
            cost_total = round(cost_in + cost_cache + cost_out, 3)

        imputed_set = {m.split("(low)")[0] for m in imputed}
        low_set = {m.split("(low)")[0] for m in imputed if m.endswith("(low)")}

        out.append({
            "Model": r.get("Model"),
            "Creator": r.get("Creator"),
            "Reasoning": r.get("Reasoning Model"),
            "Orig Intelligence Index": to_float(r.get("Intelligence Index")),
            **{m: fmt_val(eff[m], m in imputed_set, m in low_set)
               for m in metrics},
            **{m + " (norm)": round(nrm[m], 1) for m in metrics},
            "Weighted Total": round(total, 1),
            "Price 1M In": pin,
            "Price 1M Out": pout,
            "Cache Hit": pcache_eff,
            "Total $/1M": cost_total,
            "Reasoning Cost ×": (round(resolve_reasoning_multiplier(r, cost), 2)
                                 if cost_total is not None else None),
            "Imputed": ", ".join(
                f"{m}(reg)" if not m.endswith("(low)")
                else f"{m[:-5]}(reg,low)"
                for m in imputed
            ) if imputed else "",
        })

    out.sort(key=lambda x: (
        -(x["Weighted Total"] if x["Weighted Total"] is not None else -1),
        x.get("Model") or "",
        x.get("Creator") or "",
    ))

    out = [r for r in out
           if r["Weighted Total"] is not None
           and r["Weighted Total"] >= score_threshold]

    for idx, row in enumerate(out, 1):
        row["Rank"] = idx

    headers = ["Rank", "Model", "Weighted Total", "Total $/1M",
               "Reasoning Cost ×", "Creator",
               "Reasoning", "Orig Intelligence Index"]
    for _, _, subs in cats:
        for m, _ in subs:
            headers.append(m)
            headers.append(m + " (norm)")
    headers += ["Price 1M In", "Price 1M Out", "Cache Hit", "Imputed"]

    return out, headers
