# Roadmap

This roadmap records intended work, not completed capabilities.

## Stage 0: Foundation
- [x] Publish project purpose, boundaries, governance, and security principles.
- [x] Define first manifest and registry schemas.
- [x] Implement offline JSON validation.
- [ ] Establish CI and test evidence.
- [ ] Obtain independent review of the manifest schema.

## Stage 1: H-PACK local core
- [ ] Define a versioned conformance-vector format.
- [ ] Implement deterministic local test execution for trusted fixtures.
- [ ] Produce structured pass, fail, error, skipped, and not-applicable results.
- [ ] Add negative and adversarial tests.
- [ ] Publish reproducible examples.

## Stage 2: Evidence and independent verification
- [ ] Define evidence envelope and threat model.
- [ ] Bind evidence to immutable source and test-vector revisions.
- [ ] Add digest verification and canonical serialization.
- [ ] Evaluate DSSE and in-toto compatibility.
- [ ] Build a separate offline verifier.
- [ ] Document signer identity and trust-root configuration.

## Stage 3: Interoperability
- [ ] Select one narrow MCP or A2A integration profile.
- [ ] Identify two independently maintained implementations.
- [ ] Develop shared test vectors.
- [ ] Run cross-implementation differential tests.
- [ ] Publish limitations and reproducible results.

## Stage 4: Community infrastructure
- [ ] Add structured contribution formats for test vectors and findings.
- [ ] Add compatibility reports and version-difference tooling.
- [ ] Establish external maintainer review.
- [ ] Publish machine-readable agent contribution guidance.

No feature is called stable until it has documented semantics, tests, appropriate security review, compatibility policy, and reproducible release evidence. No external project is listed until its repository, licensing, provenance, and public content have been reviewed.
