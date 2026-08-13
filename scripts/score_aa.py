#!/usr/bin/env python3
"""Scoring CLI: rank deduped models by custom weights (multi-leaderboard).

The algorithm now lives in ``pipeline`` (imported below) so it is
implemented exactly once. This module is the thin CLI wrapper:
load config -> read deduped CSV -> run the shared pipeline.

Pure helpers are re-exported for import-safety / unit tests.
"""
import os
import sys

_BASE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_BASE)
SRC = os.path.join(_BASE, "merged.csv")
RESULTS_DIR = os.path.join(REPO_ROOT, "results")

# Re-export the public, import-safe helpers (single implementation
# in pipeline.config / pipeline.scoring).
from pipeline import (  # noqa: E402
    ConfigError,
    board_weights,
    fmt_val,
    load_config,
    norm,
    to_float,
    validate_config,
)

from pipeline import run_pipeline  # noqa: E402


def main():
    if not os.path.exists(SRC):
        print(f"FATAL: {SRC} missing (run parse_aa.py + dedup_aa.py first)")
        sys.exit(1)
    config_path = os.path.join(REPO_ROOT, "config.json")
    try:
        cfg = load_config(config_path)
    except ConfigError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        sys.exit(1)
    print("loaded config.json")

    validate_config(cfg)  # raises ConfigError on bad config

    import csv
    rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
    run_pipeline(rows, cfg, RESULTS_DIR)


if __name__ == "__main__":
    main()
