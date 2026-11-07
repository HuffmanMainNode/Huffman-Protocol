import json
from pathlib import Path

import pytest

from hpack.validation import DocumentValidationError, validate_manifest, validate_registry

ROOT = Path(__file__).resolve().parents[1]


def test_empty_registry_is_valid() -> None:
    validate_registry(ROOT / "registry" / "index.json")


def test_manifest_fixture_is_valid() -> None:
    validate_manifest(ROOT / "tests" / "fixtures" / "valid-manifest.json")


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
    entry = {"id": "same.protocol", "manifest": "entries/one.json"}
    path.write_text(
        json.dumps({"registry_version": "0.1.0", "updated": "2026-11-06", "entries": [entry, entry]}),
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
