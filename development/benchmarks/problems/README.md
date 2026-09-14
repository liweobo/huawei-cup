# Problem Source Gate

Historical benchmark packages may be registered in two distinct states:

- `ACCEPTED`: a user-provided local package is preserved byte-for-byte, has a
  `source.yaml` manifest, and passes raw-file existence and SHA256 checks. This
  supports reproducible testing but does not assert official provenance.
- `VERIFIED`: official provenance has been independently checked against an
  official artifact or traceable official source URL.

The 2024/C package is currently `ACCEPTED`, `artifact_origin: USER_PROVIDED`,
and `official_provenance: UNKNOWN`. It must never be rewritten as
`OFFICIAL_DIRECT`. `compliance/2026-rules.md` is a competition-rules record,
not a historical problem source. Synthetic trajectories remain valid Harness
demos but never count as historical coverage.
