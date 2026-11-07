"""Offline validation of A2A 1.0 Agent Cards using the official SDK."""

from __future__ import annotations

from pathlib import Path

from huffman_protocol.validation import DocumentValidationError, _load_json


def validate_a2a_card(path: Path) -> None:
    """Validate a local A2A 1.0 AgentCard without network access or code execution.

    The optional official A2A SDK supplies the protocol's protobuf model and
    required-field validation. This checks card structure only; it does not
    authenticate the publisher, verify JWS signatures, or contact the agent.
    """
    document = _load_json(path)
    if not isinstance(document, dict):
        raise DocumentValidationError(f"{path}: A2A AgentCard must be a JSON object")

    try:
        from a2a.types import AgentCard, InvalidParamsError
        from a2a.utils.proto_utils import validate_proto_required_fields
        from google.protobuf.json_format import ParseDict, ParseError
    except ImportError as exc:
        raise DocumentValidationError(
            "A2A card validation requires the optional official SDK; "
            'install it with: python -m pip install ".[a2a]"'
        ) from exc

    try:
        card = ParseDict(document, AgentCard(), ignore_unknown_fields=False)
        validate_proto_required_fields(card)
    except (ParseError, InvalidParamsError, TypeError, ValueError) as exc:
        raise DocumentValidationError(f"{path}: invalid A2A AgentCard: {exc}") from exc

    if not card.supported_interfaces:
        raise DocumentValidationError(
            f"{path}: A2A AgentCard must declare at least one supported interface"
        )

    versions = {interface.protocol_version for interface in card.supported_interfaces}
    if "1.0" not in versions:
        raise DocumentValidationError(
            f"{path}: no supported interface declares A2A protocolVersion '1.0'"
        )
