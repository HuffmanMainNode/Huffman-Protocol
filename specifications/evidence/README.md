# Evidence model

Version 0.1.0 is design-stage.

Evidence packages make test claims reproducible and independently checkable. The initial H-PACK verifier validates the package schema and SHA-256 digests of declared local artifacts.

## Package layout

A package is a directory containing:

- `evidence.json`: versioned metadata, immutable subject and test-suite revisions, result records, artifact paths and SHA-256 digests, and limitations.
- The artifact files referenced by `evidence.json`, stored beneath the package directory.

Verify a package locally:

```sh
huffman-protocol verify-evidence path/to/evidence-package
```

The verifier is offline and does not execute the subject, fetch repositories, or establish publisher identity. It rejects malformed metadata, mutable or malformed source revisions, duplicate artifact paths, missing files, path traversal, symlink artifacts, and digest mismatches.

## Evidence interpretation

Minimum evidence fields identify:
- Evidence format version and evidence identifier.
- Subject identifier, repository, and immutable source revision.
- Test suite identifier, version, and immutable revision.
- Individual result outcomes.
- Artifact paths and SHA-256 digests.
- Creation timestamp and known limitations.

A digest detects changes relative to a trusted digest. A signature can attribute a statement to a key under a defined trust model. Neither proves the statement is true, that the key belongs to the claimed organization, that tests were comprehensive, or that software is safe.

Independent verification means a separate verifier can validate the package and reproduce the stated checks. The current verifier checks package structure and artifact integrity only; it does not rerun tests or verify signatures.

Evidence must not contain secrets, private user data, or unnecessary operational details.
