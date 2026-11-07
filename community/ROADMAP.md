# Roadmap

This roadmap records intended work, not completed capabilities. Checkboxes are implementation claims and must be backed by code, tests, and reproducible CI.

## Stage 0: Foundation
- [x] Publish project purpose, boundaries, governance, and security principles.
- [x] Define first manifest and registry schemas.
- [x] Implement offline JSON validation.
- [x] Establish CI across Python 3.11, 3.12, and 3.13.
- [x] Build source and wheel distributions and verify isolated wheel installation.
- [ ] Obtain independent review of the manifest and evidence schemas.

## Stage 1: H-PACK local core
- [x] Define a versioned evidence package schema.
- [x] Implement offline evidence package validation and SHA-256 artifact verification.
- [x] Reject path traversal, symlink artifacts, duplicate identifiers, missing files, and digest/size mismatches.
- [x] Publish a non-claiming example evidence package.
- [ ] Define a versioned conformance-vector format.
- [ ] Implement deterministic local test execution for trusted fixtures.
- [ ] Produce structured pass, fail, error, skipped, and not-applicable results from actual test execution.
- [ ] Add reproducible adapter test fixtures.

## Stage 2: Evidence and independent verification
- [x] Bind evidence packages to immutable subject and test-suite revision identifiers.
- [x] Define artifact digests and local integrity verification.
- [ ] Define a threat model for evidence producers, signers, and verifiers.
- [ ] Evaluate DSSE and in-toto compatibility.
- [ ] Add cryptographic signing and configurable trust-root verification.
- [ ] Build a separate independent verifier.
- [ ] Document signer identity, revocation, and trust-root lifecycle.

## Stage 3: Interoperability
- [x] Select the A2A 1.0 AgentCard profile and pin upstream specification and SDK revisions.
- [x] Implement offline AgentCard structural validation using the official optional SDK.
- [ ] Identify two independently maintained implementations.
- [ ] Develop shared test vectors.
- [ ] Run cross-implementation differential tests.
- [ ] Publish limitations and reproducible results.
- [ ] Add safe, explicit network adapters only after threat-model review.

## Stage 4: Decentralized adoption
- [ ] Define a portable, content-addressed capability exchange format.
- [ ] Define peer discovery and transport profiles without requiring a central service.
- [ ] Define replay protection, identity, key rotation, and abuse controls.
- [ ] Prototype independent local nodes and test multi-implementation interoperability.
- [ ] Publish reproducible deployment instructions and offline-first operation.

No feature is called stable until it has documented semantics, tests, appropriate security review, compatibility policy, and reproducible release evidence. No external project is listed until its repository, licensing, provenance, and public content have been reviewed.
