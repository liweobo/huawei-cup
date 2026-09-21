# Implementation Notes

An export-only NameError occurred in the initial `save_solution` transfer-ratio writer: B was referenced without binding `solution["B"]`. The LP had completed and its numerical constraints were unaffected. The missing local binding was corrected and the complete experiment rerun. This is an ordinary variable-scope implementation bug, not a Skill gap. Partial exports were never selected as final evidence; only the final archived result version is active.

The rejected 3000/2400-t sparse-layout attempts are distinct from this bug: they are genuine fixed-design capacity infeasibilities and remain recorded. The 900-departure relaxation is diagnostic only and is never an eligible incumbent.

Initial regressions used a long temporary path inside the benchmark directory.
This triggered Windows path-length failures and deliberate historical-write
guards in existing2023E tests. Original logs are retained, not relabeled as
network failures. isolated_regression.py reruns byte-identical tracked tests,
Skill and required2023E fixtures in an ignored local replica with extended
Windows paths. No original test or Skill file is changed.

The workspace manifest describes repository visibility honestly. Its initial
writable_root spelling was relative while allowed_write_root was absolute.
The final spelling is normalized, preserving a copy of the original manifest.
Legacy strict clean-room validation still rejects repository visibility; this
is disclosed and not retroactively called an OS-isolated run.
