"""Scoring: min-max norm, weighted total, cost, ranking + threshold."""
from __future__ import annotations

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


def _cache_rate_for(cost, creator):
    """Real-world cache-hit-rate assumption for a model creator.

    Falls back to ``provider_cache_rates.default`` then the global
    ``cache_hit_rate``. AA does not publish per-model hit rates (hit
    rate depends on the user's prompt pattern), so this is a
    configurable usage assumption per creator.
    """
    rates = cost.get("provider_cache_rates") or {}
    if creator in rates:
        return float(rates[creator])
    if "default" in rates:
        return float(rates["default"])
    return float(cost.get("cache_hit_rate", 0.50))


def _plan_for(plans, creator):
    """Best (lowest-discount) matching subscription plan, else (1.0, "").

    A plan applies when the model's Creator is in its
    ``creator_match``; the lowest discount wins (cheapest effective
    price). Credit-value plans (e.g. GitHub Copilot) make API usage
    effectively cheaper than the list price.
    """
    best_d, best_name = 1.0, ""
    for p in plans or []:
        if creator in (p.get("creator_match") or []):
            d = float(p.get("discount") or 1.0)
            if d < best_d:
                best_d, best_name = d, p.get("name", "")
    return best_d, best_name


def _cost_terms(r, cost, cache_multiplier, cache_price_fallback, plans):
    """Compute standard vs real-world cost for one row.

    Returns (standard_total, effective_total, cache_rate, plan_name,
    pin, pout, pcache_eff):
    - standard: unit-price baseline (global cache_hit_rate, real cache
      price when known, else input × cache_multiplier).
    - effective: per-creator cache-hit rate + real cache price
      (fallback: per-creator mean, then input × cache_multiplier)
      × subscription-plan discount.
    """
    pin = to_float(r.get("Price 1M Input"))
    pout = to_float(r.get("Price 1M Output"))
    pcache = to_float(r.get("Cache Hit Price"))
    creator = (r.get("Creator") or "").strip()
    if None in (pin, pout):
        return None, None, None, "", pin, pout, None

    pcache_eff = pcache
    if pcache_eff is None and (cache_price_fallback or {}).get(creator):
        pcache_eff = cache_price_fallback[creator]
    if pcache_eff is None and pin is not None:
        pcache_eff = pin * cache_multiplier

    in_share = cost["input_share"]
    out_share = cost["output_share"]
    glob_hit = float(cost["cache_hit_rate"])
    eff_hit = _cache_rate_for(cost, creator)
    discount, plan_name = _plan_for(plans, creator)

    standard = (in_share * (1 - glob_hit) * pin
                + in_share * glob_hit * pcache_eff
                + out_share * pout)
    effective = (in_share * (1 - eff_hit) * pin
                 + in_share * eff_hit * pcache_eff
                 + out_share * pout) * discount
    return (round(standard, 3), round(effective, 3), eff_hit, plan_name,
            pin, pout, pcache_eff)


def score_board(rows, board, engine, cost, cache_multiplier, score_threshold,
                plans=None, cache_price_fallback=None):
    """Score one leaderboard. Returns (scored_rows, headers).

    ``engine`` provides stats / cur / raw / imputation_quality and
    the shared pool. No algorithm is duplicated here.

    ``rank_by`` (board config, default "score"): "score" ranks by
    Weighted Total, "value" ranks by Weighted Total / Effective $/1M
    and drops rows without an effective cost.
    """
    cats, glob = board_weights(board)
    metrics = list(glob.keys())
    rank_by = board.get("rank_by", "score")
    stats = engine.stats
    cur = engine.cur
    raw = engine.raw
    imp_q = engine.imputation_quality
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

        std_cost, eff_cost, cache_rate, plan_name, pin, pout, pcache_eff = \
            _cost_terms(r, cost, cache_multiplier, cache_price_fallback,
                        plans)
        value_score = (round(total / eff_cost, 2)
                       if eff_cost else None)

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
            "Total $/1M": std_cost,
            "Effective $/1M": eff_cost,
            "Value Score": value_score,
            "Cache Hit Rate": cache_rate,
            "Plan": plan_name,
            "AA Cost/Task": to_float(r.get("Cost Per Task")),
            "Imputed": ", ".join(
                f"{m}(reg)" if not m.endswith("(low)")
                else f"{m[:-5]}(reg,low)"
                for m in imputed
            ) if imputed else "",
        })

    if rank_by == "value":
        out = [r for r in out if r.get("Value Score") is not None]
        out.sort(key=lambda x: (-x["Value Score"],
                                x.get("Model") or "",
                                x.get("Creator") or ""))
    else:
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
               "Effective $/1M", "Value Score", "Cache Hit Rate", "Plan",
               "AA Cost/Task", "Creator", "Reasoning",
               "Orig Intelligence Index"]
    for _, _, subs in cats:
        for m, _ in subs:
            headers.append(m)
            headers.append(m + " (norm)")
    headers += ["Price 1M In", "Price 1M Out", "Cache Hit", "Imputed"]

    return out, headers
