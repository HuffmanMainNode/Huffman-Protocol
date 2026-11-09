"""Offline validation for Huffman Protocol registry documents."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

MAX_JSON_DOCUMENT_BYTES = 16 * 1024 * 1024
MAX_JSON_NESTING_DEPTH = 64


class DocumentValidationError(ValueError):
    """Raised when a document is invalid against its published schema."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DocumentValidationError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def _check_json_nesting(document: Any, source: Path) -> None:
    pending = [(document, 0)]
    while pending:
        value, depth = pending.pop()
        if depth > MAX_JSON_NESTING_DEPTH:
            raise DocumentValidationError(
                f"{source}: JSON nesting exceeds {MAX_JSON_NESTING_DEPTH} levels"
            )
        if isinstance(value, dict):
            pending.extend((child, depth + 1) for child in value.values())
        elif isinstance(value, list):
            pending.extend((child, depth + 1) for child in value)


def _load_json(path: Path) -> Any:
    try:
        with path.open("rb") as handle:
            raw = handle.read(MAX_JSON_DOCUMENT_BYTES + 1)
        if len(raw) > MAX_JSON_DOCUMENT_BYTES:
            raise DocumentValidationError(
                f"{path}: JSON document exceeds {MAX_JSON_DOCUMENT_BYTES} byte limit"
            )
        document = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
        _check_json_nesting(document, path)
        return document
    except json.JSONDecodeError as exc:
        raise DocumentValidationError(
            f"{path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    except UnicodeError as exc:
        raise DocumentValidationError(f"{path}: JSON is not valid UTF-8: {exc}") from exc
    except RecursionError as exc:
        raise DocumentValidationError(f"{path}: JSON nesting exceeds parser limits") from exc
    except OSError as exc:
        raise DocumentValidationError(f"{path}: {exc}") from exc


def _validate(document: Any, schema_name: str, source: Path) -> None:
    schema_path = files("huffman_protocol").joinpath("schemas", schema_name)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(document), key=lambda error: tuple(str(part) for part in error.path)
    )
    if errors:
        details = []
        for error in errors:
            location = "$" + "".join(
                f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.absolute_path
            )
            details.append(f"{location}: {error.message}")
        raise DocumentValidationError(
            f"{source}: document does not satisfy {schema_name}:\n- " + "\n- ".join(details)
        )


def validate_manifest(path: Path) -> None:
    """Validate one protocol manifest without network access or code execution."""
    _validate(_load_json(path), "manifest.schema.json", path)


def validate_conformance_vector(path: Path) -> None:
    """Validate one declarative conformance vector without executing it."""
    _validate(_load_json(path), "conformance-vector.schema.json", path)


def validate_registry(path: Path) -> None:
    """Validate the registry index without fetching referenced repositories."""
    document = _load_json(path)
    _validate(document, "registry.schema.json", path)
    entries = document["entries"]
    identifiers = [entry["id"] for entry in entries]
    manifests = [entry["manifest"] for entry in entries]
    if len(identifiers) != len(set(identifiers)):
        raise DocumentValidationError(f"{path}: registry contains duplicate entry identifiers")
    if len(manifests) != len(set(manifests)):
        raise DocumentValidationError(f"{path}: registry contains duplicate manifest paths")
    registry_root = path.parent.resolve()
    for entry in entries:
        manifest = entry["manifest"]
        relative_path = Path(manifest)
        parts = relative_path.parts
        if relative_path.is_absolute() or ".." in parts or "\\" in manifest:
            raise DocumentValidationError(f"{path}: unsafe manifest path: {manifest}")
        target = (registry_root / relative_path).resolve()
        try:
            target.relative_to(registry_root)
        except ValueError as exc:
            raise DocumentValidationError(
                f"{path}: manifest resolves outside registry directory: {manifest}"
            ) from exc
        if not target.is_file():
            raise DocumentValidationError(f"{path}: referenced manifest does not exist: {manifest}")
        manifest_document = _load_json(target)
        _validate(manifest_document, "manifest.schema.json", target)
        if manifest_document["id"] != entry["id"]:
            raise DocumentValidationError(
                f"{path}: registry id does not match manifest id for {manifest}"
            )
