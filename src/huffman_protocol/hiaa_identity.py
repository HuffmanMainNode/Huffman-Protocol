"""Ed25519 agent identities; private-key persistence is caller-managed."""

from __future__ import annotations

import base64
import hashlib
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def _enc(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _dec(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


@dataclass(frozen=True)
class AgentIdentity:
    private_key: Ed25519PrivateKey

    @classmethod
    def generate(cls) -> "AgentIdentity":
        return cls(Ed25519PrivateKey.generate())

    @classmethod
    def from_private_bytes(cls, value: bytes) -> "AgentIdentity":
        return cls(Ed25519PrivateKey.from_private_bytes(value))

    @property
    def private_bytes(self) -> bytes:
        return self.private_key.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption(),
        )

    @property
    def public_bytes(self) -> bytes:
        return self.private_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )

    @property
    def public_key(self) -> str:
        return _enc(self.public_bytes)

    @property
    def agent_id(self) -> str:
        return "hiaa:ed25519:" + hashlib.sha256(self.public_bytes).hexdigest()

    def sign(self, message: bytes) -> str:
        return _enc(self.private_key.sign(message))


def verify_signature(public_key: str, message: bytes, signature: str) -> bool:
    try:
        Ed25519PublicKey.from_public_bytes(_dec(public_key)).verify(_dec(signature), message)
        return True
    except (ValueError, TypeError, InvalidSignature):
        return False
