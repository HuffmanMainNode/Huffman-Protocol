"""Offline integrity verification for H-PACK evidence packages."""

from __future__ import annotations

import hashlib
import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from huffman_protocol.validation import DocumentValidationError, _load_json


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
    """Verify evidence.json and listed SHA-256 artifacts without network or code execution."""
    root = package_dir.resolve()
    if not root.is_dir():
        raise DocumentValidationError(f"{package_dir}: evidence package directory does not exist")

    manifest_path = root / "evidence.json"
    document = _load_json(manifest_path)
    _validate_evidence(document, manifest_path)

    result_ids = [result["test_id"] for result in document["results"]]
    if len(result_ids) != len(set(result_ids)):
        raise DocumentValidationError(f"{manifest_path}: duplicate test result identifiers")

    seen_paths: set[str] = set()
    for artifact in document["artifacts"]:
        relative_path = artifact["path"]
        if relative_path in seen_paths:
            raise DocumentValidationError(
                f"{manifest_path}: duplicate artifact path: {relative_path}"
            )
        seen_paths.add(relative_path)

        artifact_path = _safe_artifact_path(root, relative_path, manifest_path)
        digest = hashlib.sha256()
        size_bytes = 0
        with artifact_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                size_bytes += len(chunk)

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
