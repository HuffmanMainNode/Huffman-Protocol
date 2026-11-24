# Changelog

All notable project changes are recorded here. This file tracks repository changes; it does not imply that a package or GitHub release has been published.

## Unreleased

### Release preparation
- CI now builds source and wheel distributions, generates SHA-256 checksums, and uploads them as a downloadable workflow artifact when the Python 3.12 matrix job succeeds.
- Registry maintenance date refreshed to 2026-11-24.

### Added
- HIAA v0.1 experimental Ed25519 identity and signed-message reference implementation.
- Experimental newline-delimited JSON TCP request and signed acknowledgement transport, with loopback integration coverage.
- Machine-readable discovery metadata for implemented and not-yet-implemented capabilities.
- CI coverage for Python 3.11, 3.12, and 3.13, optional A2A AgentCard validation, distribution builds, and isolated wheel installation.

### Documentation
- Added architecture, governance, security, contribution, and roadmap guidance.
- Documented HIAA transport limitations, including plaintext transport, process-local replay protection, and unimplemented key lifecycle operations.

### Known limitations
- HIAA remains experimental and is not a production agent runtime or security certification.
- The TCP transport does not provide confidentiality or TLS peer authentication.
- Cross-process and cross-machine interoperability, durable replay state, key enrollment and rotation, and independent security review remain outstanding.
- H-PACK verifies local evidence structure and artifact digests; it does not independently establish publisher identity or rerun tests.
- A2A support is local AgentCard structural validation, not remote task exchange or signature verification.

A versioned release entry must be added only after the exact tagged source revision passes CI and the source distribution, wheel, and checksum file are attached to the GitHub release.
