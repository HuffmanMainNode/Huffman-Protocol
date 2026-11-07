# Governance

## Purpose

Huffman Protocol develops open, machine-readable infrastructure for protocol discovery, conformance testing, interoperability evaluation, and independently checkable evidence. It is not a standards authority, security certification body, identity provider, or replacement for existing standards.

## Roles

- Maintainers manage repository health, review contributions, and approve releases.
- Contributors submit code, specifications, test vectors, and evaluations.
- Independent evaluators reproduce tests and report findings without being presumed project endorsers.
- AI agents may discover, analyze, test within approved boundaries, and propose changes. They do not receive automatic merge authority.

## Decision principles

Prefer interoperability with established standards. Require evidence for technical claims. Keep specifications, implementations, and evaluations separately identifiable. Document dissent, limitations, and unresolved questions.

## Registry admission

Every entry requires:
- A canonical public non-fork source repository.
- A reviewed immutable commit or release reference.
- A relationship type: specification, implementation, adapter, or supporting tool.
- A license and provenance assessment.
- A description grounded in observable source and tests.
- Explicit maturity, limitations, and verification status.

Private repositories and unpublished material are excluded. Public visibility alone is not clearance.

## Changes and releases

Changes enter through pull requests. Maintainers review scope, tests, security, provenance, licensing, and compatibility. Breaking schema or protocol changes require versioning decisions and migration notes. Releases identify the exact source revision and test evidence.

Maintainers should disclose material conflicts of interest when evaluating their own work. Author review must not be represented as independent review.
