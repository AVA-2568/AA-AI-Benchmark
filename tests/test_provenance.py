"""Unit tests for pipeline.provenance (sha256 / count_rows / manifest)."""
import csv
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS = os.path.join(_REPO, "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from pipeline import build_manifest, count_rows, sha256, write_manifest  # noqa: E402


def test_sha256_of_known_content(tmp_path):
    p = tmp_path / "f.bin"
    p.write_bytes(b"hello")
    assert sha256(str(p)) == (
        "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e730"
        "43362938b9824"
    )
    # missing file -> None
    assert sha256(str(tmp_path / "nope.bin")) is None


def test_count_rows(tmp_path):
    p = tmp_path / "t.csv"
    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["a", "b"])
        for i in range(7):
            w.writerow([i, i * 2])
    assert count_rows(str(p)) == 7
    # missing -> 0
    assert count_rows(str(tmp_path / "nope.csv")) == 0


def test_build_manifest_fields(tmp_path):
    raw = tmp_path / "raw.csv"
    dedup = tmp_path / "dedup.csv"
    cfg = tmp_path / "config.json"
    raw.write_text("x,y\n1,2\n3,4\n", encoding="utf-8")
    dedup.write_text("x,y\n1,2\n", encoding="utf-8")
    cfg.write_text(json.dumps({"k": 1}), encoding="utf-8")
    m = build_manifest(
        parser="RSC stream",
        raw_csv=str(raw),
        dedup_csv=str(dedup),
        config_path=str(cfg),
        stale=False,
        algorithm_version="0a62096",
    )
    assert m.parser == "RSC stream"
    assert m.stale is False
    assert m.raw_rows == 2
    assert m.dedup_rows == 1
    assert m.config_sha256
    assert m.input_sha256
    assert m.algorithm_version == "0a62096"
    assert m.source_url.startswith("https://")


def test_write_manifest_roundtrip(tmp_path):
    raw = tmp_path / "raw.csv"
    dedup = tmp_path / "dedup.csv"
    cfg = tmp_path / "config.json"
    raw.write_text("x,y\n1,2\n", encoding="utf-8")
    dedup.write_text("x,y\n1,2\n", encoding="utf-8")
    cfg.write_text("{}", encoding="utf-8")
    m = build_manifest(
        parser="__next_f.push",
        raw_csv=str(raw),
        dedup_csv=str(dedup),
        config_path=str(cfg),
        stale=True,
        algorithm_version="0a62096",
    )
    out = tmp_path / "manifest.json"
    write_manifest(m, str(out))
    back = json.loads(out.read_text(encoding="utf-8"))
    assert back["parser"] == "__next_f.push"
    assert back["stale"] is True
    assert back["raw_rows"] == 1
