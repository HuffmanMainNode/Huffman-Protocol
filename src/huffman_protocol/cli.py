"""Command-line interface for local metadata validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from huffman_protocol import __version__
from huffman_protocol.validation import (
    DocumentValidationError,
    validate_manifest,
    validate_registry,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="huffman-protocol",
        description="Validate Huffman Protocol metadata locally and offline.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    manifest = commands.add_parser("validate-manifest", help="validate one manifest JSON file")
    manifest.add_argument("path", type=Path)
    registry = commands.add_parser("validate-registry", help="validate a registry index JSON file")
    registry.add_argument("path", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "validate-manifest":
            validate_manifest(args.path)
        else:
            validate_registry(args.path)
    except DocumentValidationError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print(f"VALID: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
