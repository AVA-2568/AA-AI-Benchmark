"""Provenance: hashes, manifest model and JSON writer."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
from typing import Any, Dict, Optional

from .models import BuildManifest


def sha256(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_rows(path: str) -> int:
    if not os.path.exists(path):
        return 0
    import csv
    with open(path, encoding="utf-8-sig", newline="") as f:
        return sum(1 for _ in csv.reader(f)) - 1


def build_manifest(parser, raw_csv, dedup_csv, config_path,
                     stale, algorithm_version) -> BuildManifest:
    return BuildManifest(
        run_date=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_url="https://artificialanalysis.ai/leaderboards/providers",
        parser=parser,
        input_sha256=sha256(raw_csv),
        config_sha256=sha256(config_path) or "",
        algorithm_version=algorithm_version,
        raw_rows=count_rows(raw_csv),
        dedup_rows=count_rows(dedup_csv),
        stale=stale,
    )


def write_manifest(manifest: BuildManifest, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(manifest.__dict__, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
