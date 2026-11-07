# Schema and compatibility versioning

This policy applies to machine-readable discovery descriptors, manifests, registry documents, evidence packages, conformance vectors, and adapter profiles.

## Version identifiers

- The Python distribution follows PEP 440-compatible release versions.
- Each independently evolving document format carries its own explicit version.
- JSON Schemas use stable, version-specific `$id` values. A published schema identifier is immutable.
- A document's declared format version selects exactly one schema. Validators must not silently guess or upgrade a format.

## Compatibility rules

1. **Patch:** documentation clarifications or validator fixes that do not change the accepted document language or observable semantics.
2. **Minor:** backward-compatible additions only when older validators can safely ignore the new information. This is not available for strict schemas that reject unknown fields unless the schema explicitly permits the extension.
3. **Major:** required-field changes, type changes, changed interpretation, removed fields, tightened constraints that reject previously valid documents, or any other incompatible change.

Because the current 0.1 formats use `additionalProperties: false`, adding a field can be breaking for existing validators. Such changes require a new format version and schema identifier. Do not silently edit a released schema in place.

## Experimental 0.x policy

All 0.x formats are experimental. Their maintainers may make breaking changes, but every such change must:
- increment the relevant format version;
- publish the new schema under a new immutable `$id`;
- provide a migration note and, where practical, a migration tool;
- preserve prior schemas and representative fixtures;
- test old and new versions explicitly.

## Validator behavior

Validators must:
- reject unknown format versions;
- validate against the exact selected schema;
- report the schema identifier and actionable validation paths;
- avoid network access and code execution during metadata validation;
- never infer runtime compatibility from a valid manifest.

## Deprecation

A format is deprecated only through a documented release note and machine-readable status. A removal requires a major format change or a new major release line. The registry must retain enough metadata to identify the last supported version.

## Security and trust

Schema validity is not identity verification, provenance authentication, compatibility proof, or a security certification. Cryptographic signatures and trust-root policy are separate layers and must be specified independently.
