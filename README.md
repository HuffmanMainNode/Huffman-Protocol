# Huffman Protocol

**Open protocol interoperability, conformance, and assurance infrastructure for humans and autonomous systems.**

Huffman Protocol helps developers and autonomous software systems discover, understand, test, verify, and integrate independently developed protocols through reproducible technical evidence.

## Project status

**Stage:** Foundation / experimental

This repository is an early-stage project. It does not yet provide a security certification, trust authority, production-ready interoperability guarantee, or universal protocol standard. Capabilities are considered implemented only when supported by code and tests. Verification claims must identify their evidence, scope, and limitations.

## What we are building

- A machine-readable registry of protocol manifests.
- Versioned schemas and portable conformance test vectors.
- H-PACK, a protocol compatibility and assurance toolkit.
- Independent verification of test evidence.
- Adapters and interoperability tests for existing standards.
- A community-maintained corpus of reproducible compatibility and failure cases.

## Design principles

1. **Machine-readable first:** software agents must be able to discover and interpret project metadata without scraping prose.
2. **Evidence over assertion:** distinguish declared, implemented, tested, and independently verified capabilities.
3. **Interoperate before reinventing:** build on established protocols and provenance formats where they fit.
4. **Reproducibility:** pin source revisions, dependencies, test vectors, and verification instructions.
5. **Least privilege:** discovery and evaluation are read-only by default; contributions require explicit review.
6. **Honest security claims:** signatures and passing tests do not prove that software is safe, truthful, or free of vulnerabilities.
7. **Open participation:** no paid service, proprietary hosting, or account registration is required for basic discovery and local verification.

## Start here

- [Machine-readable discovery descriptor](huffman-protocol.json)

- [Project architecture](docs/ARCHITECTURE.md)
- [Machine-readable manifest](specifications/manifest/README.md)
- [Registry index](registry/index.json)
- [Registry guidance](registry/README.md)
- [Conformance model](specifications/conformance/README.md)
- [Evidence model](specifications/evidence/README.md)
- [Schema versioning policy](specifications/VERSIONING.md)
- [A2A 1.0 integration profile](specifications/a2a/README.md)
- [Agent instructions](AGENTS.md)
- [Governance](GOVERNANCE.md)
- [Security policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Roadmap](community/ROADMAP.md)

## Repository scope

This repository is the specification, registry, tooling, and verification home. Upstream projects retain ownership of their source code and releases. Registry entries reference canonical repositories and reviewed immutable revisions; they do not copy upstream code.

Forks are not automatically catalogued. Every entry requires a relevance, visibility, licensing, provenance, and content review.

## Run locally

GitHub is the source repository and distribution point, not a required runtime host. The toolkit runs on the machine that installs it. Metadata and evidence validation are offline and require no Huffman Protocol server, account, API key, or hosted service.

Clone and install the runtime package:

```sh
git clone https://github.com/HuffmanMainNode/Huffman-Protocol.git
cd Huffman-Protocol
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
python -m pip install .
huffman-protocol --help
huffman-protocol validate-registry registry/index.json
huffman-protocol verify-evidence examples/evidence-package
```

For development and tests, install the optional development dependencies:

```sh
python -m pip install -e ".[dev]"
python -m pytest
ruff format --check .
ruff check .
```

The core validator and evidence verifier are offline. Optional A2A card validation uses the official A2A SDK to validate a local A2A 1.0 AgentCard; it does not contact the agent or verify signatures.

## Optional A2A 1.0 card validation

Install the optional official SDK integration:

```sh
python -m pip install ".[a2a]"
huffman-protocol validate-a2a-card path/to/agent-card.json
```

This validates a local AgentCard against the official A2A 1.0 protobuf model and required-field rules. It does not fetch remote cards, verify JWS signatures, or perform A2A task exchange. See the [A2A integration profile](specifications/a2a/README.md).

## Example evidence package

A deliberately non-claiming example is available at [examples/evidence-package](examples/evidence-package). It demonstrates the file layout and digest format; its result is marked `not-applicable` because it does not claim a test was executed.

## Current limitations

- The registry and toolkit are experimental.
- H-PACK can verify local evidence package structure and SHA-256 artifact integrity; it does not authenticate publishers, verify signatures, or rerun tests.
- No external implementation has yet been certified or independently verified by this project.
- Compatibility is never inferred from a manifest alone.
- Test reports are scoped evidence, not blanket security attestations.
- Networked execution of third-party code is out of scope for the initial local runner.

## License

Unless otherwise noted, project code is licensed under Apache-2.0. Individual specifications, test vectors, and third-party materials may carry separate notices. See [LICENSE](LICENSE) and file-level notices.

## Contributing

Contributions of specifications, test vectors, adapters, reproducible failures, and independent implementations are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and the security policy before submitting changes.
