"""Config loading and validation.

Replaces the old ``assert``-based checks with actionable
``ConfigError`` messages. Pure / import-safe.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List


class ConfigError(AssertionError, ValueError):
    """Raised when config.json violates a scoring invariant."""


def load_config(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise ConfigError(f"config.json not found at {path}")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def board_weights(board: Dict[str, Any]):
    """Return (CATS, GLOBAL weight map) for one leaderboard config."""
    cats = [(c["name"], c["weight"],
              [(m["name"], m["sub_weight"]) for m in c["metrics"]])
            for c in board["categories"]]
    glob = {}
    for _, cw, subs in cats:
        for m, sw in subs:
            glob[m] = cw * sw
    return cats, glob


def cost_params(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve the cost block with sensible defaults.

    New keys (reasoning-aware cost):
    - ``reasoning_output_multiplier``: output-term multiplier applied to
      reasoning models that have no recognized thinking-level suffix.
    - ``thinking_multipliers``: optional map {level: multiplier} for
      graded thinking effort (minimal/low/medium/high/xhigh/max).
    """
    cost = cfg.get("cost", {})
    return {
        "input_share": cost.get("input_share", 0.70),
        "output_share": cost.get("output_share", 0.30),
        "cache_hit_rate": cost.get("cache_hit_rate", 0.50),
        "reasoning_output_multiplier": cost.get(
            "reasoning_output_multiplier", 1.0),
        "thinking_multipliers": cost.get("thinking_multipliers", {}) or {},
    }


def to_float(v):
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        if v in ("", "None", "null"):
            return None
    try:
        return float(v)
    except Exception:
        return None


def imputation_params(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve imputation / cost-fallback parameters with defaults."""
    imp = cfg.get("imputation", {})
    fb = cfg.get("cost_fallback", {})
    return {
        "max_iters": imp.get("max_iters", 100),
        "relative_tolerance": imp.get("relative_tolerance", 0.005),
        "stable_rounds": imp.get("stable_rounds", 3),
        "damping": imp.get("damping", 0.5),
        "clip_quantile": imp.get("clip_quantile", 0.95),
        "cache_hit_multiplier": fb.get("cache_hit_multiplier", 0.1),
    }


def validate_config(cfg: Dict[str, Any]) -> bool:
    """Fail fast on bad config with actionable validation errors."""
    try:
        cost = cfg["cost"]
        pool = cfg["imputation_pool"]
        boards = cfg["leaderboards"]
    except KeyError as exc:
        raise ConfigError(f"missing config field: {exc.args[0]}") from exc
    imp = cfg.get("imputation", {})
    fb = cfg.get("cost_fallback", {})
    if not isinstance(pool, list) or len(pool) != len(set(pool)):
        raise ConfigError("imputation_pool must be a list of unique metric names")
    if not 0 <= cfg.get("score_threshold", -1) <= 100:
        raise ConfigError("score_threshold must be in [0, 100]")
    if cfg.get("ridge_alpha", 0) <= 0:
        raise ConfigError("ridge_alpha must be > 0")
    if cfg.get("imputation_min_samples", 0) < 3:
        raise ConfigError("imputation_min_samples must be >= 3")
    if not 0 < imp.get("max_iters", 0):
        raise ConfigError("imputation.max_iters must be > 0")
    if not 0 < imp.get("relative_tolerance", 0):
        raise ConfigError("imputation.relative_tolerance must be > 0")
    if not 1 <= imp.get("stable_rounds", 0):
        raise ConfigError("imputation.stable_rounds must be >= 1")
    if not 0 < imp.get("damping", 0) <= 1:
        raise ConfigError("imputation.damping must be in (0, 1]")
    if not 0 < imp.get("clip_quantile", 0) <= 1:
        raise ConfigError("imputation.clip_quantile must be in (0, 1]")
    if not 0 < fb.get("cache_hit_multiplier", 0) <= 1:
        raise ConfigError("cost_fallback.cache_hit_multiplier must be in (0, 1]")
    if (not 0 <= cost.get("input_share", -1) <= 1
            or not 0 <= cost.get("output_share", -1) <= 1):
        raise ConfigError("cost shares must be in [0, 1]")
    if abs(cost["input_share"] + cost["output_share"] - 1.0) >= 1e-6:
        raise ConfigError(
            "cost.input_share + cost.output_share must equal 1, "
            f"got {cost['input_share'] + cost['output_share']}"
        )
    if not 0 <= cost.get("cache_hit_rate", -1) <= 1:
        raise ConfigError(
            f"cost.cache_hit_rate must be in [0, 1], "
            f"got {cost.get('cache_hit_rate')}"
        )
    # reasoning-aware cost knobs (optional; validated only if present)
    if ("reasoning_output_multiplier" in cost
            and cost["reasoning_output_multiplier"] <= 0):
        raise ConfigError(
            "cost.reasoning_output_multiplier must be > 0"
        )
    for lvl, mult in (cost.get("thinking_multipliers") or {}).items():
        if not isinstance(mult, (int, float)) or mult <= 0:
            raise ConfigError(
                f"cost.thinking_multipliers['{lvl}'] must be > 0"
            )
    for bkey, board in boards.items():
        cats, glob = board_weights(board)
        if abs(sum(glob.values()) - 1.0) >= 1e-9:
            raise ConfigError(
                f"[{bkey}] global weights sum={sum(glob.values())}, must be 1.0"
            )
        for name, _, subs in cats:
            s = sum(sw for _, sw in subs)
            if abs(s - 1.0) >= 1e-6:
                raise ConfigError(
                    f"[{bkey}] category {name} sub_weight sum={s}, "
                    "must be 1.0"
                )
        for m in glob:
            if m not in pool:
                raise ConfigError(
                    f"[{bkey}] metric '{m}' not in imputation_pool — "
                    "add it to the pool"
                )
    return True
