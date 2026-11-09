"""Command-line interface for local metadata and evidence validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from huffman_protocol import __version__
from huffman_protocol.a2a import validate_a2a_card
from huffman_protocol.evidence import verify_evidence
from huffman_protocol.validation import (
    DocumentValidationError,
    validate_conformance_vector,
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

    vector = commands.add_parser(
        "validate-conformance-vector", help="validate one declarative conformance vector offline"
    )
    vector.add_argument("path", type=Path)

    evidence = commands.add_parser(
        "verify-evidence", help="verify an offline H-PACK evidence package"
    )
    evidence.add_argument(
        "path",
        type=Path,
        help="directory containing evidence.json and its artifacts",
    )

    a2a_card = commands.add_parser(
        "validate-a2a-card", help="validate a local A2A 1.0 AgentCard offline"
    )
    a2a_card.add_argument("path", type=Path, help="local AgentCard JSON file")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "validate-conformance-vector":
            validate_conformance_vector(args.path)
        elif args.command == "validate-manifest":
            validate_manifest(args.path)
        elif args.command == "validate-registry":
            validate_registry(args.path)
        elif args.command == "verify-evidence":
            verify_evidence(args.path)
        else:
            validate_a2a_card(args.path)
    except DocumentValidationError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1

    print(f"VALID: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
