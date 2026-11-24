# Huffman Independent Agent Architecture (HIAA)

**Status:** experimental specification, version 0.1.0.  
**Implementation status:** initial local Ed25519 identity and signed-envelope primitives. No transport or production runtime is claimed.

## Problem addressed

HIAA targets four concrete interoperability and security problems:

1. **Identity ambiguity:** derive a stable agent identifier from a public-key fingerprint.
2. **Message impersonation and tampering:** sign message payloads and verify them before processing.
3. **Replay:** reject recently accepted duplicate message identifiers and stale messages.
4. **Excessive authority:** require each receiver to enforce its own capability allowlist.

A signature demonstrates possession of a private key for a particular message. It does not prove the operator's real-world identity, honesty, safety, or authorization outside the receiver's local policy. HIAA does not solve model hallucinations, compromised endpoints, key theft, or malicious intent.

## Relationship to existing standards

- **A2A** remains the agent discovery and task-interaction protocol. HIAA does not redefine AgentCards or task semantics.
- **MCP** remains a tool and context integration protocol. HIAA does not replace MCP servers or tool schemas.
- **Ed25519** supplies signatures through the established Python cryptography package. No custom cryptography is introduced.
- **H-PACK** can package test outputs and conformance evidence. HIAA does not turn a digest into independent certification.
- **Transport** is deliberately unspecified in this initial profile. A later transport profile can use an existing reviewed standard.

## Signed message profile

The signed payload contains version, message_id, sender, recipient, capability, issued_at (Unix seconds), and a JSON body. The envelope carries the payload, base64url raw Ed25519 public key, and base64url signature. The signature covers a domain-separation prefix and deterministic UTF-8 JSON.

The initial deterministic encoding uses sorted keys, compact separators, UTF-8 characters, and rejection of non-finite numbers. It is profile-specific and **does not claim RFC 8785 JSON Canonicalization Scheme compliance**. Cross-language interoperability requires this encoding to be independently implemented and tested or a separately versioned canonicalization profile.

## Local reference implementation

Install the development package:

    python -m pip install -e ".[dev]"

Example:

    from huffman_protocol.hiaa_identity import AgentIdentity
    from huffman_protocol.hiaa_message import create_envelope, verify_envelope

    sender = AgentIdentity.generate()
    receiver = AgentIdentity.generate()
    envelope = create_envelope(sender, receiver.agent_id, "status.read", {"status": "ready"})
    assert verify_envelope(envelope)

Private-key persistence is caller-managed. The implementation does not write keys to disk, establish trust roots, rotate or revoke keys, or authenticate the operator behind a public key.

## Replay and authorization

ReplayCache is an in-memory, process-local guard. Production deployments need durable, concurrency-safe replay state. A capability label is a request, not a grant. Each receiver must compare it against its own allowlist.

## Security and implementation limits

- No network transport, peer discovery, handshake, encryption, or task execution is implemented.
- Ed25519 signatures do not encrypt message contents.
- Public-key self-identification is not a trust relationship; enrollment and trust roots remain deployment policy.
- Key backup, rotation, revocation, and compromise recovery are not implemented.
- Timestamp checks require reasonably synchronized clocks.
- Replay state is volatile and local to one process.
- The message body has no universal application schema.
- Local verification does not execute third-party code.

## Conformance requirements

A conforming implementation must demonstrate independent key generation, stable key-derived identifiers, cross-receiver signature verification, tamper rejection, sender mismatch rejection, timestamp enforcement, duplicate-message rejection, and receiver-controlled capability denial.

This initial Python implementation is a reference primitive, not a complete multi-device agent runtime. A later transport profile must demonstrate two independently installed processes exchanging messages over a real transport, including reconnect and failure behavior, before claiming peer-to-peer operation.
