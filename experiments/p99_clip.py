#!/usr/bin/env python3
"""Compare P95 vs P99 imputation clipping without changing official outputs.

The imputation algorithm now lives in ``scripts/pipeline`` (imported
below). This experiment reuses that single implementation; only the
``clip_quantile`` parameter differs between the two runs.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts" / "aa_providers_dedup.csv"
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
ROWS = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))

# Make ``pipeline`` importable when run as a standalone script.
sys.path.insert(0, str(ROOT / "scripts"))

from pipeline import (  # noqa: E402
    ImputationEngine,
    board_weights,
    imputation_params,
    norm,
)

POOL = CFG["imputation_pool"]
BOARDS = CFG["leaderboards"]
THRESHOLD = CFG["score_threshold"]
IP = imputation_params(CFG)


def build_params(clip_quantile: float) -> dict:
    """Engine params resolved from config, with clip_quantile overridden."""
    return {
        "ridge_alpha": CFG["ridge_alpha"],
        "imputation_min_samples": CFG["imputation_min_samples"],
        "standardize_features": CFG.get("standardize_features", True),
        "clip_quantile": clip_quantile,
        "damping": IP["damping"],
    }


def run_experiment(cap_quantile: float) -> dict:
    """Run scoring with a selected cap (clip) quantile.

    Reuses the shared ``ImputationEngine`` so the cross-feature ridge
    imputation, z-score standardization, damping and convergence test are
    implemented exactly once. Only ``clip_quantile`` differs from the
    official run.
    """
    params = build_params(cap_quantile)
    engine = ImputationEngine(ROWS, POOL, params)
    converged_iter, max_delta = engine.run(
        IP["max_iters"], IP["relative_tolerance"], IP["stable_rounds"])

    outputs = {}
    for board_key, board in BOARDS.items():
        _, weights = board_weights(board)
        metrics = list(weights)
        output = []
        for i, row in enumerate(ROWS):
            effective = {
                m: (engine.raw[m][i] if engine.raw[m][i] is not None
                     else engine.cur[m][i])
                for m in metrics
            }
            normalized = {
                m: norm(effective[m], engine.stats[m][0], engine.stats[m][1])
                for m in metrics
            }
            total = round(sum(weights[m] * normalized[m] for m in metrics), 1)
            if total >= THRESHOLD:
                output.append({"Model": row.get("Model"), "Score": total})
        output.sort(key=lambda item: item["Score"], reverse=True)
        for rank, r in enumerate(output, 1):
            r["Rank"] = rank
        outputs[board_key] = output

    return {"iter": converged_iter, "delta": max_delta, "out": outputs}


def main() -> None:
    """Print P95/P99 impact summary."""
    base = run_experiment(0.95)
    alt = run_experiment(0.99)
    print(f"rows={len(ROWS)}")
    print(f"P95 converged_iter={base['iter']} max_delta={base['delta']:.6f}")
    print(f"P99 converged_iter={alt['iter']} max_delta={alt['delta']:.6f}")
    for board_key in BOARDS:
        p95_rows = base["out"][board_key]
        p99_rows = alt["out"][board_key]
        p95_map = {row["Model"]: row for row in p95_rows}
        p99_map = {row["Model"]: row for row in p99_rows}
        common = set(p95_map) & set(p99_map)
        score_deltas = sorted(
            [
                (model, p99_map[model]["Score"] - p95_map[model]["Score"],
                 p95_map[model]["Score"], p99_map[model]["Score"])
                for model in common
            ],
            key=lambda item: abs(item[1]),
            reverse=True,
        )[:8]
        rank_deltas = sorted(
            [
                (model, p99_map[model]["Rank"] - p95_map[model]["Rank"],
                 p95_map[model]["Rank"], p99_map[model]["Rank"])
                for model in common
            ],
            key=lambda item: abs(item[1]),
            reverse=True,
        )[:8]
        top15_p95 = [row["Model"] for row in p95_rows[:15]]
        top15_p99 = [row["Model"] for row in p99_rows[:15]]
        print(f"\n[{board_key}] P95_rows={len(p95_rows)} P99_rows={len(p99_rows)} common={len(common)}")
        print(f"entered={sorted(set(p99_map) - set(p95_map))[:8]}")
        print(f"exited={sorted(set(p95_map) - set(p99_map))[:8]}")
        print(f"top15_same={top15_p95 == top15_p99}; top15_overlap={len(set(top15_p95) & set(top15_p99))}/15")
        print("top5_P95=" + " | ".join(f"{row['Rank']}.{row['Model']} {row['Score']}" for row in p95_rows[:5]))
        print("top5_P99=" + " | ".join(f"{row['Rank']}.{row['Model']} {row['Score']}" for row in p99_rows[:5]))
        print("max_score_delta=" + "; ".join(
            f"{model}: {old}->{new} ({delta:+.1f})"
            for model, delta, old, new in score_deltas
        ))
        print("max_rank_delta=" + "; ".join(
            f"{model}: {old}->{new} ({delta:+d})"
            for model, delta, old, new in rank_deltas
        ))


if __name__ == "__main__":
    main()
