# Evidence model

Version 0.1.0 is design-stage.

Evidence packages are intended to make test claims reproducible and independently checkable.

Minimum evidence fields should include:
- Evidence format version.
- Subject identifier and immutable source revision.
- Test suite and vector-set identifiers and revisions.
- Tool and dependency versions.
- Relevant environment details.
- Individual results and raw-output digests.
- Creation timestamp and declared clock source.
- Verifier identity and procedure, when applicable.
- Known limitations and omitted evidence.

A digest can detect changes relative to a trusted digest. A signature can attribute a statement to a key under a defined trust model. Neither proves the statement is true, that the key belongs to the claimed organization, that tests were comprehensive, or that software is safe.

Independent verification means a separate verifier can validate the package and reproduce the stated checks. It does not prove all behavior of the subject system.

Evidence must not contain secrets, private user data, or unnecessary operational details.
