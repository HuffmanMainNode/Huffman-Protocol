# Architecture

## System boundaries

Huffman Protocol has four independently versioned concerns:

1. Discovery: a static registry index and per-project manifests.
2. Specification: versioned schemas, interfaces, and conformance-vector formats.
3. Evaluation: local metadata validation, evidence integrity checks, and future conformance adapters.
4. Evidence: portable records identifying subject revision, test inputs, tools, outputs, and verification procedure.

## Data flow

Registry index -> Manifest -> Schema validation -> Candidate selection -> Conformance profile -> Approved test environment -> Structured results -> Evidence package -> Independent verification.

The current implementation covers offline manifest and registry validation plus offline evidence-package schema and artifact-integrity verification. Parsing rejects duplicate JSON keys; evidence inputs are bounded by fixed resource ceilings and symlinked manifests are rejected. It does not execute conformance tests, rerun test suites, verify signatures, or establish publisher identity. Later stages are design targets and must not be described as implemented until code and tests exist.

## Trust boundaries

- Registry content and evidence packages are untrusted input.
- JSON parsers reject duplicate object keys rather than silently selecting one value.
- Evidence verification enforces fixed manifest, artifact-count, per-artifact, and total-artifact size ceilings.
- Metadata and evidence validation do not access the network.
- A manifest does not authorize code execution.
- A valid evidence digest establishes consistency with the digest recorded in that same package, not the truth of the test claim or the identity of its publisher.
- An external test subject must not execute without a separately designed isolation boundary and explicit approval.
- Evidence consumers choose their own trust roots and acceptance policy.
- Maintainer review is not independent security certification.

## Compatibility strategy

Adapters should test and connect existing protocols rather than replace them. Candidate integrations include MCP and A2A, subject to version-specific review. Software provenance formats such as SLSA, in-toto, and DSSE should be reused where their semantics fit.

## Initial implementation

The Python package provides offline validation for manifest and registry JSON documents using JSON Schema Draft 2020-12. H-PACK also validates versioned evidence package metadata and verifies SHA-256 digests for local evidence artifacts. It intentionally does not fetch source repositories or execute external code.
