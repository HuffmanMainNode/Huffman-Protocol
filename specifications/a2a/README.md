# A2A 1.0 integration profile

## Scope

Huffman Protocol's first agent-to-agent integration targets the Agent2Agent (A2A) Protocol 1.0 AgentCard. A2A is an external open standard; this repository does not redefine it.

The upstream protocol specification is pinned to:

- Repository: https://github.com/a2aproject/A2A
- Commit: `9fff3e08ab33bb7674e7d98fc7c08ae8592bb4bd`
- Protocol release: 1.0.0
- License: Apache-2.0

The optional Python integration uses the official SDK:

- Repository: https://github.com/a2aproject/a2a-python
- Commit: `28f8a62f25d46067ae846329a42a60c820fa927e`
- SDK release: 1.3.0
- License: Apache-2.0
- Compatibility: A2A 1.0, with upstream 0.3 compatibility support

The exact commits and capabilities are recorded in `registry/index.json` and its referenced manifests. Registry verification status remains `not-evaluated`; pinning a source revision is provenance metadata, not independent certification.

## Install and use

The integration is optional. The core package remains lightweight:

```sh
python -m pip install ".[a2a]"
huffman-protocol validate-a2a-card examples/a2a-v1.0/agent-card.json
```

The adapter:
- parses the local JSON document with duplicate-key and size/depth protections;
- uses the official SDK's A2A 1.0 protobuf AgentCard model;
- rejects unknown fields and invalid field types;
- invokes the SDK's required-field validation;
- requires at least one supported interface declaring protocol version `1.0`.

## Explicit limits

This is offline structural validation only. It does not:

- fetch an AgentCard from `/.well-known/agent-card.json`;
- resolve DNS or open network connections;
- verify JWS signatures or establish a trust root;
- authenticate the agent or its operator;
- test whether the declared endpoint is reachable;
- send messages, exchange tasks, stream events, or configure push notifications;
- execute agent code.

A valid card means that the local document conforms to the selected SDK model and required-field rules. It does not prove that the described agent exists, is available, is safe, or implements its declared capabilities.

A2A 1.0 defines AgentCard signatures using JWS and JSON Canonicalization. Signature verification is a separate future milestone requiring an explicit local trust-store format, algorithm allowlist, key-rotation and revocation policy, and adversarial tests. The current command does not claim signature verification.

## Version policy

This profile targets A2A 1.0 only. A 0.3 card must be handled by a separately versioned compatibility profile, not silently accepted as 1.0. When the upstream SDK or protocol changes, update the pinned source revision, compatibility record, fixtures, and tests through a reviewed pull request.
