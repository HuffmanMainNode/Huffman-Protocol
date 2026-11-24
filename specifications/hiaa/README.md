# Huffman Independent Agent Architecture (HIAA)

**Status:** experimental specification, version 0.1.0.  
**Implementation status:** Ed25519 identity, signed-envelope primitives, and an experimental TCP request/acknowledgement transport. No production runtime is claimed.

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
- **Transport** currently has an experimental newline-delimited JSON TCP reference implementation. It is not a replacement for a reviewed production transport or encrypted channel.

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

ReplayCache is an in-memory, process-local guard keyed by the pair of sender identity and message ID. Production deployments need durable, concurrency-safe replay state. A capability label is a request, not a grant. Each receiver must compare it against its own allowlist.

## Security and implementation limits

- The experimental TCP transport carries signed request/acknowledgement envelopes, but does not provide encryption, TLS peer authentication, peer discovery, durable delivery, or task execution.
- Ed25519 signatures do not encrypt message contents.
- Public-key self-identification is not a trust relationship; the TCP receiver requires an explicit sender allowlist and the sender must pin the expected receiver identity. Enrollment exchange remains operator-managed.
- Key backup, rotation, revocation, and compromise recovery are not implemented.
- Timestamp checks require reasonably synchronized clocks.
- Replay state is volatile and local to one process.
- The message body has no universal application schema.
- Local verification does not execute third-party code.

## Conformance requirements

A conforming implementation must demonstrate independent key generation, stable key-derived identifiers, cross-receiver signature verification, tamper rejection, sender mismatch rejection, timestamp enforcement, duplicate-message rejection, and receiver-controlled capability denial.

The Python implementation now includes a TCP request/acknowledgement reference transport and loopback integration tests. Separate-process, separate-machine interoperability, reconnect behavior, and production network hardening remain required before claiming a production peer-to-peer runtime.


## Experimental TCP transport

The reference package now includes `hiaa_transport.py`, a newline-delimited JSON TCP transport for one signed request and one signed acknowledgement per connection. The receiver verifies the sender signature, intended recipient, timestamp, enrolled sender identity, and local capability policy; it rejects duplicate message IDs through its replay cache. The sender verifies the receiver's signed acknowledgement against its pinned expected peer identity and confirms that it refers to the original message.

A minimal receiver can be run as a separate process:

```python
from huffman_protocol.hiaa_identity import AgentIdentity
from huffman_protocol.hiaa_transport import HIAARequestServer

identity = AgentIdentity.generate()
server = HIAARequestServer(
    ("127.0.0.1", 8765),
    identity,
    {"status.read"},
    lambda body: {"status": "ready"},
    trusted_senders={"hiaa:ed25519:<ENROLLED_SENDER_FINGERPRINT>"},
)
print(identity.agent_id)
server.serve_forever()
```

A separately installed sender process can load its own operator-managed identity, construct an envelope with `create_envelope`, and call `send_envelope(("127.0.0.1", 8765), envelope, expected_peer=receiver_agent_id)`. The receiver must configure the sender's exact agent ID in `trusted_senders`; the sender must pin the receiver's expected agent ID as `expected_peer`. These values must be exchanged and verified out of band. This profile does not provide automatic trust discovery.

**Transport security warning:** this initial TCP transport does not encrypt traffic or authenticate the remote host at the TLS layer. Signatures protect message integrity and key possession, not confidentiality. Use loopback, a trusted network, or an independently configured encrypted tunnel. Do not expose the listener directly to an untrusted network.

The loopback integration tests exercise two independently generated identities over an actual TCP socket. The current integration test runs both endpoints in one test process; it does not yet prove separate-process or separate-machine deployment, durable replay protection, reconnect policy, key lifecycle, or production network hardening.
