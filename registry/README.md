# Registry

The registry is a curated, machine-readable index of public protocol specifications and implementations.

## Read order

1. Read `index.json`.
2. Load only the manifest paths listed in its `entries`.
3. Validate each manifest with `huffman-protocol validate-manifest PATH`.
4. Treat every claim as declared metadata until separate test evidence exists.

## Entry policy

- Each entry points to a canonical public, non-fork repository.
- Each source is pinned to an immutable commit SHA; a branch name or release tag is not a substitute.
- The relationship field distinguishes a specification from an implementation, adapter, or supporting tool.
- The verification status is explicit. `not-evaluated` means this project has not tested the entry.
- A registry entry never authorizes dependency installation, code execution, network access, or trust.
- Licenses and source provenance must be reviewed before adding entries.

## Current entries

The initial entries reference the A2A 1.0 specification and its official Python SDK. They are indexed for discovery, not certified by Huffman Protocol. See [the A2A integration profile](../specifications/a2a/README.md) for the scope of the local card validator.

Run the offline registry validator:

```sh
huffman-protocol validate-registry registry/index.json
```
