import hashlib
import json
from pathlib import Path

import pytest

from huffman_protocol.evidence import (
    MAX_EVIDENCE_ARTIFACT_BYTES,
    MAX_EVIDENCE_MANIFEST_BYTES,
    verify_evidence,
)
from huffman_protocol.validation import DocumentValidationError


def make_package(root: Path, artifact: bytes = b"captured test output") -> Path:
    root.mkdir()
    (root / "artifacts").mkdir()
    (root / "artifacts" / "result.txt").write_bytes(artifact)
    document = {
        "evidence_version": "0.1.0",
        "id": "example.evidence",
        "created_at": "2026-11-06T12:00:00Z",
        "subject": {
            "id": "example.protocol",
            "repository": "https://example.org/protocol",
            "commit": "a" * 40,
        },
        "test_suite": {
            "id": "example.conformance",
            "version": "0.1.0",
            "revision": "b" * 40,
        },
        "results": [{"test_id": "vector-001", "outcome": "pass"}],
        "artifacts": [
            {
                "path": "artifacts/result.txt",
                "sha256": hashlib.sha256(artifact).hexdigest(),
                "size_bytes": len(artifact),
            }
        ],
        "limitations": ["This package does not establish publisher identity."],
    }
    (root / "evidence.json").write_text(json.dumps(document), encoding="utf-8")
    return root


def test_valid_evidence_package_passes(tmp_path: Path) -> None:
    verify_evidence(make_package(tmp_path / "package"))


def test_modified_artifact_is_rejected(tmp_path: Path) -> None:
    pkg = make_package(tmp_path / "package")
    (pkg / "artifacts" / "result.txt").write_bytes(b"replaced test output")
    with pytest.raises(DocumentValidationError, match="SHA-256 mismatch"):
        verify_evidence(pkg)


def test_missing_artifact_is_rejected(tmp_path: Path) -> None:
    pkg = make_package(tmp_path / "package")
    (pkg / "artifacts" / "result.txt").unlink()
    with pytest.raises(DocumentValidationError, match="does not exist"):
        verify_evidence(pkg)


def test_parent_traversal_is_rejected(tmp_path: Path) -> None:
    pkg = make_package(tmp_path / "package")
    document = json.loads((pkg / "evidence.json").read_text(encoding="utf-8"))
    document["artifacts"][0]["path"] = "../outside.txt"
    (pkg / "evidence.json").write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(
        DocumentValidationError,
        match="does not satisfy|unsafe artifact path",
    ):
        verify_evidence(pkg)


def test_duplicate_artifact_paths_are_rejected(tmp_path: Path) -> None:
    pkg = make_package(tmp_path / "package")
    document = json.loads((pkg / "evidence.json").read_text(encoding="utf-8"))
    document["artifacts"].append(document["artifacts"][0])
    (pkg / "evidence.json").write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(DocumentValidationError, match="duplicate artifact target"):
        verify_evidence(pkg)


def test_symlink_artifact_is_rejected(tmp_path: Path) -> None:
    pkg = make_package(tmp_path / "package")
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    (pkg / "artifacts" / "linked.txt").symlink_to(outside)

    document = json.loads((pkg / "evidence.json").read_text(encoding="utf-8"))
    document["artifacts"][0]["path"] = "artifacts/linked.txt"
    document["artifacts"][0]["sha256"] = hashlib.sha256(b"outside").hexdigest()
    (pkg / "evidence.json").write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(DocumentValidationError, match="symlink artifact paths"):
        verify_evidence(pkg)


def test_invalid_subject_revision_is_rejected(tmp_path: Path) -> None:
    pkg = make_package(tmp_path / "package")
    document = json.loads((pkg / "evidence.json").read_text(encoding="utf-8"))
    document["subject"]["commit"] = "mutable-branch"
    (pkg / "evidence.json").write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(DocumentValidationError, match="does not satisfy"):
        verify_evidence(pkg)


def test_missing_package_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(DocumentValidationError, match="directory does not exist"):
        verify_evidence(tmp_path / "missing")


def test_declared_artifact_size_mismatch_is_rejected(tmp_path: Path) -> None:
    pkg = make_package(tmp_path / "package")
    document = json.loads((pkg / "evidence.json").read_text(encoding="utf-8"))
    document["artifacts"][0]["size_bytes"] += 1
    (pkg / "evidence.json").write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(DocumentValidationError, match="size mismatch"):
        verify_evidence(pkg)


def test_duplicate_test_result_ids_are_rejected(tmp_path: Path) -> None:
    pkg = make_package(tmp_path / "package")
    document = json.loads((pkg / "evidence.json").read_text(encoding="utf-8"))
    document["results"].append(document["results"][0])
    (pkg / "evidence.json").write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(DocumentValidationError, match="duplicate test result identifiers"):
        verify_evidence(pkg)


def test_cli_verify_evidence_command_succeeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from huffman_protocol.cli import main

    package = make_package(tmp_path / "package")
    monkeypatch.setattr("sys.argv", ["huffman-protocol", "verify-evidence", str(package)])
    assert main() == 0
    assert "VALID:" in capsys.readouterr().out


def test_equivalent_artifact_paths_are_rejected(tmp_path: Path) -> None:
    pkg = make_package(tmp_path / "package")
    document = json.loads((pkg / "evidence.json").read_text(encoding="utf-8"))
    alias = dict(document["artifacts"][0])
    alias["path"] = "artifacts/./result.txt"
    document["artifacts"].append(alias)
    (pkg / "evidence.json").write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(DocumentValidationError, match="duplicate artifact target"):
        verify_evidence(pkg)


def test_invalid_evidence_json_is_rejected(tmp_path: Path) -> None:
    pkg = tmp_path / "package"
    pkg.mkdir()
    (pkg / "evidence.json").write_text('{"evidence_version":', encoding="utf-8")
    with pytest.raises(DocumentValidationError, match="invalid JSON"):
        verify_evidence(pkg)


def test_duplicate_json_object_keys_are_rejected(tmp_path: Path) -> None:
    pkg = make_package(tmp_path / "package")
    manifest = pkg / "evidence.json"
    manifest.write_text(
        '{"evidence_version":"0.1.0","evidence_version":"0.1.0"}',
        encoding="utf-8",
    )
    with pytest.raises(DocumentValidationError, match="duplicate JSON object key"):
        verify_evidence(pkg)


def test_symlink_evidence_manifest_is_rejected(tmp_path: Path) -> None:
    pkg = make_package(tmp_path / "package")
    manifest = pkg / "evidence.json"
    external_manifest = tmp_path / "external-evidence.json"
    manifest.replace(external_manifest)
    manifest.symlink_to(external_manifest)
    with pytest.raises(DocumentValidationError, match="manifest symlinks"):
        verify_evidence(pkg)


def test_oversized_evidence_manifest_is_rejected(tmp_path: Path) -> None:
    pkg = tmp_path / "package"
    pkg.mkdir()
    manifest = pkg / "evidence.json"
    manifest.write_bytes(b" " * (MAX_EVIDENCE_MANIFEST_BYTES + 1))
    with pytest.raises(DocumentValidationError, match="manifest exceeds"):
        verify_evidence(pkg)


def test_oversized_artifact_is_rejected_before_hashing(tmp_path: Path) -> None:
    pkg = make_package(tmp_path / "package")
    artifact = pkg / "artifacts" / "result.txt"
    with artifact.open("r+b") as handle:
        handle.truncate(MAX_EVIDENCE_ARTIFACT_BYTES + 1)
    with pytest.raises(DocumentValidationError, match="artifact exceeds"):
        verify_evidence(pkg)
