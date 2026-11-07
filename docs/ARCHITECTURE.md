# Architecture

## System boundaries

Huffman Protocol has four independently versioned concerns:

1. Discovery: a static registry index and per-project manifests.
2. Specification: versioned schemas, interfaces, and conformance-vector formats.
3. Evaluation: local validation, test adapters, and compatibility reporting.
4. Evidence: portable records identifying subject revision, test inputs, tools, outputs, and verification procedure.

## Data flow

Registry index -> Manifest -> Schema validation -> Candidate selection -> Conformance profile -> Approved test environment -> Structured results -> Evidence package -> Independent verification.

The current implementation covers local JSON Schema validation only. Later stages are design targets and must not be described as implemented until code and tests exist.

## Trust boundaries

- Registry content is untrusted input.
- Manifest validation does not access the network.
- A manifest does not authorize code execution.
- External test execution must be isolated and separately approved.
- Evidence consumers choose their own trust roots and acceptance policy.
- Maintainer review is not independent security certification.

## Compatibility strategy

Adapters should test and connect existing protocols rather than replace them. Candidate integrations include MCP and A2A, subject to version-specific review. Software provenance formats such as SLSA, in-toto, and DSSE should be reused where their semantics fit.

## Initial implementation

The first Python package provides offline validation for manifest and registry JSON documents using JSON Schema Draft 2020-12. It intentionally does not fetch source repositories or execute external code.
