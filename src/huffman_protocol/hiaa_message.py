"""Signed HIAA message envelopes and local replay/capability checks."""
from __future__ import annotations
import hashlib
import json
import threading
import time
from typing import Any
from huffman_protocol.hiaa_identity import AgentIdentity, verify_signature

_DOMAIN = b"HUFFMAN-HIAA-MESSAGE-V0.1\\x00"

def canonical_payload(payload: dict[str, Any]) -> bytes:
    """Profile-specific deterministic JSON; this is not RFC 8785 JCS."""
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")
    return json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def _agent_id(public_key: str) -> str:
    import base64
    raw = base64.urlsafe_b64decode(public_key + "=" * (-len(public_key) % 4))
    return "hiaa:ed25519:" + hashlib.sha256(raw).hexdigest()

def create_envelope(identity: AgentIdentity, recipient: str, capability: str, body: dict[str, Any], *, issued_at: int | None = None, message_id: str | None = None) -> dict[str, Any]:
    timestamp = int(time.time()) if issued_at is None else issued_at
    payload = {
        "version": "0.1.0",
        "message_id": message_id or hashlib.sha256(identity.public_bytes + str(timestamp).encode() + canonical_payload(body)).hexdigest(),
        "sender": identity.agent_id,
        "recipient": recipient,
        "capability": capability,
        "issued_at": timestamp,
        "body": body,
    }
    return {"payload": payload, "public_key": identity.public_key, "signature": identity.sign(_DOMAIN + canonical_payload(payload))}

def verify_envelope(envelope: dict[str, Any], *, now: int | None = None, max_age: int = 300) -> bool:
    try:
        payload, public_key, signature = envelope["payload"], envelope["public_key"], envelope["signature"]
        if not isinstance(payload, dict) or payload.get("version") != "0.1.0" or payload.get("sender") != _agent_id(public_key):
            return False
        issued_at = payload["issued_at"]
        if not isinstance(issued_at, int) or isinstance(issued_at, bool):
            return False
        current = int(time.time()) if now is None else now
        if issued_at > current + 30 or current - issued_at > max_age:
            return False
        return verify_signature(public_key, _DOMAIN + canonical_payload(payload), signature)
    except (KeyError, TypeError, ValueError):
        return False

class ReplayCache:
    """Volatile, process-local replay guard. Durable state is deployment-owned."""
    def __init__(self, capacity: int = 10000) -> None:
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._seen: dict[str, int] = {}
        self._lock = threading.Lock()

    def accept(self, envelope: dict[str, Any], *, now: int | None = None) -> bool:
        if not verify_envelope(envelope, now=now):
            return False
        current = int(time.time()) if now is None else now
        message_id = envelope["payload"]["message_id"]
        with self._lock:
            self._seen = {key: expiry for key, expiry in self._seen.items() if expiry >= current}
            if message_id in self._seen:
                return False
            if len(self._seen) >= self.capacity:
                del self._seen[min(self._seen, key=self._seen.get)]
            self._seen[message_id] = current + 300
            return True

def authorize(envelope: dict[str, Any], allowed_capabilities: set[str], *, now: int | None = None) -> bool:
    return (
        verify_envelope(envelope, now=now)
        and isinstance(envelope["payload"].get("capability"), str)
        and envelope["payload"]["capability"] in allowed_capabilities
    )
