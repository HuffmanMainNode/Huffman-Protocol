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
