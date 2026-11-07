# Protocol manifest specification

Version 0.1.0 is experimental.

A manifest is a machine-readable description of one public protocol-related artifact. It describes declared properties; it does not prove implementation or behavior.

Required distinctions:
- relationship: specification, implementation, adapter, or supporting tool.
- status: proposed, experimental, active, stable, deprecated, or retired.
- verification status: not-evaluated, declared, implemented, tested, or independently-verified.

A registry entry must reference a canonical public non-fork repository and an exact 40-character Git commit SHA. A release tag is useful metadata but is mutable and cannot replace a pinned commit.

The normative schema is packaged at src/hpack/schemas/manifest.schema.json. Validate locally after installing the package with its development dependencies using: hpack validate-manifest path/to/manifest.json

Validation is offline. It does not fetch a repository, execute code, verify ownership, or establish the truth of a manifest's claims. Unknown fields are rejected in version 0.1.0 to prevent silent ambiguity.
