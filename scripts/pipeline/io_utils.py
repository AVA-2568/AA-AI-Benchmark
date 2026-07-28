"""CSV / JSON IO helpers for the pipeline."""
from __future__ import annotations

import csv
import json
import os
from typing import Any, Dict, List


def read_rows(path: str) -> List[Dict[str, Any]]:
    with open(path, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_scored_csv(out_rows, headers, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=headers, extrasaction="ignore")
        w.writeheader()
        w.writerows(out_rows)
    os.replace(tmp, path)


def write_validation(board_key: str, board_val: Dict[str, Any],
                  path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(board_val, fh, ensure_ascii=False, indent=2)
