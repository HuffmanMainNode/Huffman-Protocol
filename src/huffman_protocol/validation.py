"""Offline validation for Huffman Protocol registry documents."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


class DocumentValidationError(ValueError):
    """Raised when a document is invalid against its published schema."""


def _load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        raise DocumentValidationError(
            f"{path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
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
