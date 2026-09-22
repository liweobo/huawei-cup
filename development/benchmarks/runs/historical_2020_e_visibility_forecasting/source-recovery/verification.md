# Verification

Baseline main: `a65aaac1d2986b8dcb3b6d9ae9c754f14d45623b`. Skill tree: `8deb5278e19862738d8f04f21d8a7b6d3f5eb45e`. The original [integrity-before.json](integrity-before.json) is retained unchanged.

| Check | Result / scope |
|---|---|
| Official competition page and published package credentials | PASS; current HTTP 200, exact title/link/password checks |
| Full official package hash, file signature and archive safety | NOT_PERFORMED_PACKAGE_UNAVAILABLE; no empty-file hash or synthetic manifest substituted |
| Six existing mirror-file SHA256 / size / Git blob hashes | PASS against frozen source manifest |
| Existing AMOS and highway ZIP safety / CRC | PASS; read-only member inspection and CRC streaming, no extraction |
| Frozen history and Skill | PASS; 1009 files verified against baseline objects, including payload SHA256/size for 3 hydrated Git LFS files |
| Scope of modifications | Source-recovery metadata/reports only; no model, skill, run-001 or previous historical asset edits |
| Manifest consistency / metadata hashes / staged-file allowlist | See [verification.json](verification.json) and [metadata-manifest.json](metadata-manifest.json), generated and checked before commit |
| Full modelling/Python suite | NOT_RERUN; no model or shipped Python change; stage instruction requires source/integrity checks only |

The initial raw Git-blob comparison encountered hydrated LFS content in existing 2024C assets. Its bytes were then correctly checked against the committed LFS pointer's SHA256 and size; no frozen file was changed. [integrity-after.json](integrity-after.json) records each protected path and tree.

Rechecking the two existing ZIP files is not an official-package safety check. Empty official `e_entries` means not enumerated. Download caches, browser profiles, cookies, raw transport records and prior preview artifacts remain ignored and are excluded from the commit. No excellent papers or solution material are committed.

Git delivery follows the original authorization: stage only this report set, commit on main, push normally and verify the remote SHA. The resulting commit SHA and push outcome are reported separately; a commit cannot contain its own hash.
