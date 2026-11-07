import json
from pathlib import Path

import pytest

from huffman_protocol.validation import (
    DocumentValidationError,
    validate_manifest,
    validate_registry,
)

ROOT = Path(__file__).resolve().parents[1]


def test_empty_registry_is_valid() -> None:
    validate_registry(ROOT / "registry" / "index.json")


def test_manifest_fixture_is_valid() -> None:
    validate_manifest(ROOT / "tests" / "fixtures" / "valid-manifest.json")


def test_independent_verification_requires_evidence(tmp_path: Path) -> None:
    manifest = json.loads((ROOT / "tests" / "fixtures" / "valid-manifest.json").read_text())
    manifest["verification"] = {"status": "independently-verified"}
    path = tmp_path / "unsupported-claim.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(DocumentValidationError, match="does not satisfy"):
        validate_manifest(path)


def test_invalid_manifest_is_rejected() -> None:
    with pytest.raises(DocumentValidationError, match="does not satisfy"):
        validate_manifest(ROOT / "tests" / "fixtures" / "invalid-manifest.json")


def test_invalid_json_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text('{"id": ', encoding="utf-8")
    with pytest.raises(DocumentValidationError, match="invalid JSON"):
        validate_registry(path)


def test_invalid_registry_date_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    path.write_text(
        json.dumps({"registry_version": "0.1.0", "updated": "not-a-date", "entries": []}),
        encoding="utf-8",
    )
    with pytest.raises(DocumentValidationError, match="does not satisfy"):
        validate_registry(path)


def test_duplicate_registry_ids_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    entries = [
        {"id": "same.protocol", "manifest": "entries/one.json"},
        {"id": "same.protocol", "manifest": "entries/two.json"},
    ]
    path.write_text(
        json.dumps({"registry_version": "0.1.0", "updated": "2026-11-06", "entries": entries}),
        encoding="utf-8",
    )
    with pytest.raises(DocumentValidationError, match="duplicate entry identifiers"):
        validate_registry(path)


def test_registry_path_traversal_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    entry = {"id": "safe.protocol", "manifest": "../outside.json"}
    path.write_text(
        json.dumps({"registry_version": "0.1.0", "updated": "2026-11-06", "entries": [entry]}),
        encoding="utf-8",
    )
    with pytest.raises(DocumentValidationError, match="unsafe manifest path"):
        validate_registry(path)


def test_registry_resolves_and_validates_manifest(tmp_path: Path) -> None:
    entries_dir = tmp_path / "entries"
    entries_dir.mkdir()
    manifest = json.loads((ROOT / "tests" / "fixtures" / "valid-manifest.json").read_text())
    (entries_dir / "example.json").write_text(json.dumps(manifest), encoding="utf-8")
    registry = tmp_path / "index.json"
    registry.write_text(
        json.dumps({
            "registry_version": "0.1.0",
            "updated": "2026-11-06",
            "entries": [{"id": manifest["id"], "manifest": "entries/example.json"}],
        }),
        encoding="utf-8",
    )
    validate_registry(registry)


def test_registry_rejects_manifest_id_mismatch(tmp_path: Path) -> None:
    entries_dir = tmp_path / "entries"
    entries_dir.mkdir()
    manifest = json.loads((ROOT / "tests" / "fixtures" / "valid-manifest.json").read_text())
    (entries_dir / "example.json").write_text(json.dumps(manifest), encoding="utf-8")
    registry = tmp_path / "index.json"
    registry.write_text(
        json.dumps({
            "registry_version": "0.1.0",
            "updated": "2026-11-06",
            "entries": [{"id": "different.protocol", "manifest": "entries/example.json"}],
        }),
        encoding="utf-8",
    )
    with pytest.raises(DocumentValidationError, match="does not match manifest id"):
        validate_registry(registry)


def test_registry_rejects_missing_manifest(tmp_path: Path) -> None:
    registry = tmp_path / "index.json"
    registry.write_text(
        json.dumps({
            "registry_version": "0.1.0",
            "updated": "2026-11-06",
            "entries": [{"id": "missing.protocol", "manifest": "entries/missing.json"}],
        }),
        encoding="utf-8",
    )
    with pytest.raises(DocumentValidationError, match="does not exist"):
        validate_registry(registry)
