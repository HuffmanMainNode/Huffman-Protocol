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
