import json
from pathlib import Path

import pytest

from huffman_protocol.validation import (
    MAX_JSON_DOCUMENT_BYTES,
    DocumentValidationError,
    validate_conformance_vector,
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
        json.dumps(
            {
                "registry_version": "0.1.0",
                "updated": "2026-11-06",
                "entries": [{"id": manifest["id"], "manifest": "entries/example.json"}],
            }
        ),
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
        json.dumps(
            {
                "registry_version": "0.1.0",
                "updated": "2026-11-06",
                "entries": [{"id": "different.protocol", "manifest": "entries/example.json"}],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(DocumentValidationError, match="does not match manifest id"):
        validate_registry(registry)


def test_registry_rejects_missing_manifest(tmp_path: Path) -> None:
    registry = tmp_path / "index.json"
    registry.write_text(
        json.dumps(
            {
                "registry_version": "0.1.0",
                "updated": "2026-11-06",
                "entries": [{"id": "missing.protocol", "manifest": "entries/missing.json"}],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(DocumentValidationError, match="does not exist"):
        validate_registry(registry)


def test_duplicate_json_object_keys_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "duplicate-keys.json"
    path.write_text('{"id":"first","id":"second"}', encoding="utf-8")
    with pytest.raises(DocumentValidationError, match="duplicate JSON object key"):
        validate_manifest(path)


def test_oversized_metadata_json_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "oversized.json"
    with path.open("wb") as handle:
        handle.truncate(MAX_JSON_DOCUMENT_BYTES + 1)
    with pytest.raises(DocumentValidationError, match="JSON document exceeds"):
        validate_manifest(path)


def test_excessively_nested_json_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "deep.json"
    path.write_text("[" * 3000 + "0" + "]" * 3000, encoding="utf-8")
    with pytest.raises(DocumentValidationError, match="nesting exceeds"):
        validate_manifest(path)


def test_conformance_vector_fixture_is_valid() -> None:
    validate_conformance_vector(ROOT / "tests" / "fixtures" / "valid-conformance-vector.json")


def test_conformance_vector_rejects_unbounded_timeout(tmp_path: Path) -> None:
    vector = json.loads((ROOT / "tests" / "fixtures" / "valid-conformance-vector.json").read_text())
    vector["timeout_seconds"] = 301
    path = tmp_path / "unbounded-vector.json"
    path.write_text(json.dumps(vector), encoding="utf-8")
    with pytest.raises(DocumentValidationError, match="does not satisfy"):
        validate_conformance_vector(path)


def test_conformance_vector_rejects_missing_resource_limits(tmp_path: Path) -> None:
    vector = json.loads((ROOT / "tests" / "fixtures" / "valid-conformance-vector.json").read_text())
    del vector["resource_limits"]
    path = tmp_path / "missing-limits.json"
    path.write_text(json.dumps(vector), encoding="utf-8")
    with pytest.raises(DocumentValidationError, match="does not satisfy"):
        validate_conformance_vector(path)


def test_conformance_vector_cli_validates_without_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from huffman_protocol.cli import main

    path = ROOT / "tests" / "fixtures" / "valid-conformance-vector.json"
    monkeypatch.setattr("sys.argv", ["huffman-protocol", "validate-conformance-vector", str(path)])
    assert main() == 0
    assert "VALID:" in capsys.readouterr().out


def test_conformance_vector_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    path = tmp_path / "duplicate-vector.json"
    path.write_text('{"vector_version":"0.1.0","vector_version":"0.1.0"}', encoding="utf-8")
    with pytest.raises(DocumentValidationError, match="duplicate JSON object key"):
        validate_conformance_vector(path)


def test_conformance_vector_rejects_oversized_json(tmp_path: Path) -> None:
    path = tmp_path / "oversized-vector.json"
    with path.open("wb") as handle:
        handle.truncate(MAX_JSON_DOCUMENT_BYTES + 1)
    with pytest.raises(DocumentValidationError, match="JSON document exceeds"):
        validate_conformance_vector(path)


def test_conformance_vector_rejects_excessive_nesting(tmp_path: Path) -> None:
    path = tmp_path / "deep-vector.json"
    path.write_text('{"input":' + "[" * 100 + "0" + "]" * 100 + "}", encoding="utf-8")
    with pytest.raises(DocumentValidationError, match="nesting exceeds"):
        validate_conformance_vector(path)

def test_discovery_descriptor_lists_conformance_vector_validation() -> None:
    descriptor = json.loads((ROOT / "huffman-protocol.json").read_text(encoding="utf-8"))
    assert "offline-conformance-vector-schema-validation" in descriptor["implemented_capabilities"]
    assert "huffman-protocol validate-conformance-vector PATH" in descriptor["package"]["commands"]
