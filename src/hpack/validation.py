"""Offline validation for Huffman Protocol registry documents."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


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
    schema_path = files("hpack").joinpath("schemas", schema_name)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.path))
    if errors:
        details = []
        for error in errors:
            location = "$" + "".join(
                f"[{part}]" if isinstance(part, int) else f".{part}"
                for part in error.absolute_path
            )
            details.append(f"{location}: {error.message}")
        raise DocumentValidationError(
            f"{source}: document does not satisfy {schema_name}:\n- "
            + "\n- ".join(details)
        )


def validate_manifest(path: Path) -> None:
    """Validate one protocol manifest without network access or code execution."""
    _validate(_load_json(path), "manifest.schema.json", path)


def validate_registry(path: Path) -> None:
    """Validate the registry index without fetching referenced repositories."""
    _validate(_load_json(path), "registry.schema.json", path)
