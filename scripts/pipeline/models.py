"""Typed data models for the scoring pipeline.

These dataclasses are the single source of truth for the shapes that flow
through config loading, imputation, scoring and provenance. They are
import-safe (no numpy / sklearn at import time).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class MetricSpec:
    """One metric used by the leaderboards / imputation pool."""
    name: str
    category: str
    weight: float
    allow_imputation: bool


@dataclass(frozen=True)
class CategorySpec:
    name: str
    weight: float
    metrics: List[MetricSpec]


@dataclass(frozen=True)
class LeaderboardConfig:
    key: str
    title: str
    output_csv: str
    validation_json: str
    categories: List[CategorySpec]


@dataclass
class ImputationResult:
    """Per-metric imputation diagnostics."""
    n_train: int
    converged_iter: Optional[int] = None
    max_delta: Optional[float] = None


@dataclass
class ScoredModel:
    model: str
    creator: Optional[str]
    weighted_total: Optional[float]
    rank: Optional[int] = None
    imputed: List[str] = field(default_factory=list)


@dataclass
class BuildManifest:
    run_date: str
    source_url: str
    parser: Optional[str]
    input_sha256: Optional[str]
    config_sha256: str
    algorithm_version: str
    raw_rows: int
    dedup_rows: int
    stale: bool
