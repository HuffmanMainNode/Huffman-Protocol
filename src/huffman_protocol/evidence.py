"""Offline integrity verification for H-PACK evidence packages."""

from __future__ import annotations

import hashlib
import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from huffman_protocol.validation import DocumentValidationError, _load_json

MAX_EVIDENCE_MANIFEST_BYTES = 4 * 1024 * 1024
MAX_EVIDENCE_ARTIFACTS = 256
MAX_EVIDENCE_ARTIFACT_BYTES = 128 * 1024 * 1024
MAX_EVIDENCE_TOTAL_ARTIFACT_BYTES = 512 * 1024 * 1024


def _validate_evidence(document: Any, source: Path) -> None:
    schema_path = files("huffman_protocol").joinpath("schemas", "evidence.schema.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: tuple(str(part) for part in error.path),
    )
    if errors:
        details = []
        for error in errors:
            location = "$" + "".join(
                f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.absolute_path
            )
            details.append(f"{location}: {error.message}")
        raise DocumentValidationError(
            f"{source}: evidence does not satisfy evidence.schema.json:\n- " + "\n- ".join(details)
        )


def _safe_artifact_path(root: Path, value: str, source: Path) -> Path:
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts or "\\" in value:
        raise DocumentValidationError(f"{source}: unsafe artifact path: {value}")

    candidate = root
    for part in relative.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise DocumentValidationError(
                f"{source}: symlink artifact paths are not allowed: {value}"
            )

    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise DocumentValidationError(
            f"{source}: artifact resolves outside evidence package: {value}"
        ) from exc

    if not resolved.is_file():
        raise DocumentValidationError(
            f"{source}: artifact does not exist or is not a file: {value}"
        )
    return resolved


def verify_evidence(package_dir: Path) -> None:
    """Verify an offline evidence package within documented resource limits."""
    root = package_dir.resolve()
    if not root.is_dir():
        raise DocumentValidationError(f"{package_dir}: evidence package directory does not exist")

    manifest_path = root / "evidence.json"
    if manifest_path.is_symlink():
        raise DocumentValidationError(
            f"{manifest_path}: evidence manifest symlinks are not allowed"
        )
    try:
        manifest_size = manifest_path.stat().st_size
    except OSError as exc:
        raise DocumentValidationError(f"{manifest_path}: {exc}") from exc
    if manifest_size > MAX_EVIDENCE_MANIFEST_BYTES:
        raise DocumentValidationError(
            f"{manifest_path}: evidence manifest exceeds {MAX_EVIDENCE_MANIFEST_BYTES} byte limit"
        )

    document = _load_json(manifest_path)
    _validate_evidence(document, manifest_path)

    if len(document["artifacts"]) > MAX_EVIDENCE_ARTIFACTS:
        raise DocumentValidationError(
            f"{manifest_path}: artifact count exceeds {MAX_EVIDENCE_ARTIFACTS}"
        )

    result_ids = [result["test_id"] for result in document["results"]]
    if len(result_ids) != len(set(result_ids)):
        raise DocumentValidationError(f"{manifest_path}: duplicate test result identifiers")

    seen_targets: set[Path] = set()
    total_artifact_bytes = 0
    for artifact in document["artifacts"]:
        relative_path = artifact["path"]
        artifact_path = _safe_artifact_path(root, relative_path, manifest_path)
        if artifact_path in seen_targets:
            raise DocumentValidationError(
                f"{manifest_path}: duplicate artifact target: {relative_path}"
            )
        seen_targets.add(artifact_path)

        try:
            declared_file_size = artifact_path.stat().st_size
        except OSError as exc:
            raise DocumentValidationError(f"{artifact_path}: {exc}") from exc
        if declared_file_size > MAX_EVIDENCE_ARTIFACT_BYTES:
            raise DocumentValidationError(
                f"{manifest_path}: artifact exceeds {MAX_EVIDENCE_ARTIFACT_BYTES} byte limit: "
                f"{relative_path}"
            )
        if total_artifact_bytes + declared_file_size > MAX_EVIDENCE_TOTAL_ARTIFACT_BYTES:
            raise DocumentValidationError(
                f"{manifest_path}: total artifact bytes exceed "
                f"{MAX_EVIDENCE_TOTAL_ARTIFACT_BYTES} byte limit"
            )

        digest = hashlib.sha256()
        size_bytes = 0
        with artifact_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                size_bytes += len(chunk)
                if size_bytes > MAX_EVIDENCE_ARTIFACT_BYTES:
                    raise DocumentValidationError(
                        f"{manifest_path}: artifact grew beyond byte limit while reading: "
                        f"{relative_path}"
                    )
                if total_artifact_bytes + size_bytes > MAX_EVIDENCE_TOTAL_ARTIFACT_BYTES:
                    raise DocumentValidationError(
                        f"{manifest_path}: total artifact bytes exceed "
                        f"{MAX_EVIDENCE_TOTAL_ARTIFACT_BYTES} byte limit"
                    )

        total_artifact_bytes += size_bytes
        if "size_bytes" in artifact and artifact["size_bytes"] != size_bytes:
            raise DocumentValidationError(
                f"{manifest_path}: size mismatch for {relative_path}: "
                f"expected {artifact['size_bytes']}, got {size_bytes}"
            )

        actual = digest.hexdigest()
        if actual != artifact["sha256"]:
            raise DocumentValidationError(
                f"{manifest_path}: SHA-256 mismatch for {relative_path}: "
                f"expected {artifact['sha256']}, got {actual}"
            )
