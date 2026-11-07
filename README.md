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
- [Registry](registry/index.json)
- [Conformance model](specifications/conformance/README.md)
- [Evidence model](specifications/evidence/README.md)
- [Agent instructions](AGENTS.md)
- [Governance](GOVERNANCE.md)
- [Security policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Roadmap](community/ROADMAP.md)

## Repository scope

This repository is the specification, registry, tooling, and verification home. Upstream projects retain ownership of their source code and releases. Registry entries reference canonical repositories and reviewed immutable revisions; they do not copy upstream code.

Forks are not automatically catalogued. Every entry requires a relevance, visibility, licensing, provenance, and content review.

## Local validation

Install the package and development tools, then validate the registry and run the tests:

```sh
python -m pip install -e ".[dev]"
huffman-protocol validate-registry registry/index.json
python -m pytest
```

The validator is offline. It validates schemas, manifest references, identifier consistency, and safe relative paths. It does not fetch or execute upstream code.

## Current limitations

- The registry and toolkit are experimental.
- No external implementation has yet been certified or independently verified by this project.
- Compatibility is never inferred from a manifest alone.
- Test reports are scoped evidence, not blanket security attestations.
- Networked execution of third-party code is out of scope for the initial local runner.

## License

Unless otherwise noted, project code is licensed under Apache-2.0. Individual specifications, test vectors, and third-party materials may carry separate notices. See [LICENSE](LICENSE) and file-level notices.

## Contributing

Contributions of specifications, test vectors, adapters, reproducible failures, and independent implementations are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and the security policy before submitting changes.
