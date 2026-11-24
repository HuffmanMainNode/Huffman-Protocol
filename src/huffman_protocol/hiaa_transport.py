"""Experimental newline-delimited JSON transport for HIAA envelopes.

This transport provides message authentication, not confidentiality. Use a
trusted network or an independently configured encrypted tunnel.
"""

from __future__ import annotations

import json
import socket
import socketserver
from collections.abc import Callable
from typing import Any

from huffman_protocol.hiaa_identity import AgentIdentity
from huffman_protocol.hiaa_message import (
    ReplayCache,
    authorize,
    create_envelope,
    verify_envelope,
)

MAX_MESSAGE_BYTES = 1_048_576


class _HIAARequestHandler(socketserver.StreamRequestHandler):
    server: "HIAARequestServer"

    def handle(self) -> None:
        raw = self.rfile.readline(MAX_MESSAGE_BYTES + 1)
        if not raw or len(raw) > MAX_MESSAGE_BYTES or not raw.endswith(b"\n"):
            self._write({"accepted": False, "error": "invalid_frame"})
            return
        try:
            envelope = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._write({"accepted": False, "error": "invalid_json"})
            return
        if not isinstance(envelope, dict):
            self._write({"accepted": False, "error": "invalid_envelope"})
            return
        if not authorize(
            envelope,
            self.server.allowed_capabilities,
            expected_recipient=self.server.identity.agent_id,
        ):
            self._write({"accepted": False, "error": "rejected"})
            return
        if not self.server.replay_cache.accept(envelope):
            self._write({"accepted": False, "error": "replay_or_expired"})
            return
        sender = envelope["payload"]["sender"]
        message_id = envelope["payload"]["message_id"]
        try:
            result = self.server.handler(envelope["payload"]["body"])
        except Exception:
            self._write({"accepted": False, "error": "handler_failed"})
            return
        acknowledgement = create_envelope(
            self.server.identity,
            sender,
            "message.ack",
            {"accepted": True, "message_id": message_id, "result": result},
        )
        self._write(acknowledgement)

    def _write(self, value: dict[str, Any]) -> None:
        self.wfile.write(
            json.dumps(
                value, ensure_ascii=False, allow_nan=False, separators=(",", ":")
            ).encode("utf-8")
            + b"\n"
        )


class HIAARequestServer(socketserver.ThreadingTCPServer):
    """Threaded TCP receiver. Bind to loopback unless network exposure is intended."""

    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 32

    def __init__(
        self,
        address: tuple[str, int],
        identity: AgentIdentity,
        allowed_capabilities: set[str],
        handler: Callable[[dict[str, Any]], dict[str, Any]],
        *,
        replay_cache: ReplayCache | None = None,
    ) -> None:
        self.identity = identity
        self.allowed_capabilities = set(allowed_capabilities)
        self.handler = handler
        self.replay_cache = replay_cache or ReplayCache()
        super().__init__(address, _HIAARequestHandler)


def send_envelope(
    address: tuple[str, int],
    envelope: dict[str, Any],
    *,
    timeout: float = 5.0,
) -> dict[str, Any]:
    """Send one signed envelope and verify the receiver's signed acknowledgement."""
    request = json.dumps(
        envelope, ensure_ascii=False, allow_nan=False, separators=(",", ":")
    ).encode("utf-8") + b"\n"
    if len(request) > MAX_MESSAGE_BYTES:
        raise ValueError("message exceeds HIAA transport frame limit")
    with socket.create_connection(address, timeout=timeout) as connection:
        connection.settimeout(timeout)
        connection.sendall(request)
        with connection.makefile("rb") as stream:
            response = stream.readline(MAX_MESSAGE_BYTES + 1)
    if not response or len(response) > MAX_MESSAGE_BYTES or not response.endswith(b"\n"):
        raise ConnectionError("receiver returned an invalid or oversized frame")
    acknowledgement = json.loads(response)
    if (
        not isinstance(acknowledgement, dict)
        or acknowledgement.get("accepted") is False
    ):
        raise PermissionError("receiver rejected the HIAA message")
    sender = envelope["payload"]["sender"]
    if not verify_envelope(
        acknowledgement, expected_recipient=sender
    ):
        raise ConnectionError("receiver acknowledgement signature or recipient is invalid")
    ack_payload = acknowledgement["payload"]
    if (
        ack_payload.get("capability") != "message.ack"
        or ack_payload.get("body", {}).get("message_id")
        != envelope["payload"].get("message_id")
        or ack_payload.get("body", {}).get("accepted") is not True
    ):
        raise ConnectionError("receiver acknowledgement does not match the request")
    return acknowledgement
