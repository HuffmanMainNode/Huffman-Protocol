# Release procedure

This document defines the reproducible release procedure for the Huffman Protocol Python distribution.

## Current release line

- Distribution: `huffman-protocol`
- Current package version: `0.1.0`
- Maturity: experimental
- Supported Python: `>=3.11`
- Release assets: source distribution, wheel, and SHA-256 checksum manifest

Do not describe HIAA as production-ready. Its TCP profile is plaintext, replay state is process-local, and key lifecycle plus independent cross-machine interoperability remain incomplete. See [HIAA](../specifications/hiaa/README.md) and [SECURITY.md](../SECURITY.md).

## Required release gates

1. Confirm the working tree and intended source revision are clean and reviewed.
2. Confirm the version in `pyproject.toml` matches the intended tag.
3. Run the complete CI workflow on the exact release commit.
4. Confirm Python 3.11, 3.12, and 3.13 test, formatting, lint, build, and isolated-wheel-install checks pass.
5. Confirm the A2A adapter job passes.
6. Download the `huffman-protocol-0.1.0-dist` workflow artifact from the successful run.
7. Verify the artifact contains the source archive, wheel, and `SHA256SUMS`; verify the checksums after download.
8. Create the annotated tag `v0.1.0` at the exact verified commit.
9. Create a GitHub release from that tag and attach the verified source archive, wheel, and checksum manifest.
10. Add the release date, source commit, CI run URL, and artifact names to the changelog.

## Reproducibility

Builds are performed by the checked-in GitHub Actions workflow. The workflow artifact is retained for 30 days; it is a CI handoff, not a permanent release. Published GitHub release assets must be attached separately.

## Do not bypass a failed gate

A failed, missing, or inaccessible CI result is not a pass. Do not tag or publish based on an earlier commit's green run. Do not weaken tests to make a release pass. If the release workflow or branch-protection settings cannot be verified, record that limitation and keep the release unpublished.

## Branch governance

Protect `main` with required pull requests and required CI checks before scaling outside contributions. Confirm the actual GitHub branch rules in repository settings; documentation alone does not enable protection.
