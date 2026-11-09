# Conformance model

**Vector metadata status:** implemented in protocol version 0.1.0.
**Execution engine status:** not implemented.

Conformance testing evaluates an implementation against a versioned specification and test profile. A declarative vector is a test description, not proof that a test was executed.

## Vector contract

The machine-readable contract is `src/huffman_protocol/schemas/conformance-vector.schema.json`. Validate a local vector with:

```bash
huffman-protocol validate-conformance-vector tests/fixtures/valid-conformance-vector.json
```

Each vector defines a stable identifier, vector-set version, target interface and version, input data, observable assertions, preconditions, permitted side effects, timeout, resource bounds, determinism, expected outcome, and safety classification.

Result states:
- pass: observed output satisfies the defined assertion.
- fail: observed output violates the assertion.
- error: execution did not complete as specified.
- skipped: not run, with a reason.
- not-applicable: outside the declared profile.

## Trust and execution boundary

The validator checks JSON metadata against the published schema. It does not run test code, download dependencies, clone repositories, connect to remote systems, or establish that a declared expected outcome is true.

A result must not be inferred from a manifest. Compatibility requires actual tests against identified implementation revisions and retained evidence.

Any future execution engine must be a separate component with isolation, least privilege, resource limits, no ambient credentials, explicit network policy, bounded output, and independently verifiable execution records. Arbitrary third-party repository code must never execute as a side effect of validation.
