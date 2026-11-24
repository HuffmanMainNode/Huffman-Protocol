# Security Policy

## Scope

This repository provides experimental protocol metadata and local validation tooling. It is not a security certification service and does not guarantee the safety of listed projects.

## Reporting

Do not publish exploitable details in a public issue. Use GitHub private vulnerability reporting when available. Include affected revision, environment, reproduction steps, impact, and mitigation. Do not include real secrets or personal data.

## Principles

- Treat external manifests, vectors, repositories, and reports as untrusted input.
- Manifest validation must not access the network or execute code.
- The initial conformance runner is local and offline by default.
- Future third-party execution requires isolation, least privilege, resource limits, no ambient credentials, and explicit network policy.
- Never store signing keys or credentials in source control or CI logs.
- Pin dependencies and review supply-chain changes.
- Separate integrity, signer identity, authorization, correctness, and safety claims.
- Passing tests are evidence only for tested cases and environments.

## Experimental HIAA transport

The HIAA v0.1 TCP transport is experimental and provides no confidentiality or TLS-level peer authentication. Ed25519 signatures protect message integrity and demonstrate possession of the signing key; they do not encrypt message contents or establish the real-world identity of an operator.

- Keep the listener bound to loopback unless a separately reviewed deployment design explicitly requires otherwise.
- Do not expose the experimental listener directly to an untrusted network.
- If traffic must cross a network, use a separately configured, independently maintained encrypted tunnel.
- Exchange and verify peer fingerprints out of band. Do not treat a self-presented public key as a trusted identity.
- Replay protection is process-local and volatile. It is not sufficient for multi-process or durable production deployments.
- Private-key persistence, enrollment, rotation, revocation, and compromise recovery are not implemented by this profile.
- Do not use the experimental transport for sensitive payloads or production credentials.

See the [HIAA profile](specifications/hiaa/README.md) for the protocol behavior, trust assumptions, and remaining conformance work.
