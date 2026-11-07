# Conformance model

Version 0.1.0 is design-stage.

Conformance testing evaluates an implementation against a versioned specification and test profile.

Each test vector should define a stable identifier, vector-set version, target interface and version, input and expected observable behavior, preconditions, permitted side effects, timeout and resource bounds, determinism, expected failure behavior, and safety classification.

Result states:
- pass: observed output satisfies the defined assertion.
- fail: observed output violates the assertion.
- error: execution did not complete as specified.
- skipped: not run, with a reason.
- not-applicable: outside the declared profile.

A result must not be inferred from a manifest. Compatibility requires actual tests against identified implementation revisions.

The initial toolkit validates metadata and local test data only. It does not download or execute third-party projects. Future execution must use isolation, least privilege, resource limits, no ambient credentials, and explicit network policy.
