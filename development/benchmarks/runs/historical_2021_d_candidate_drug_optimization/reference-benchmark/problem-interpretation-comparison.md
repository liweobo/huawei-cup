# Problem and Source Interpretation Comparison

## Disease and target wording

| evidence | breast cancer | pancreatic cancer | ERα / estrogen receptor alpha | effect on frozen source decision |
|---|---|---|---|---|
| Frozen source provenance | internal problem text and workbooks support ERα; mirrored filename says pancreatic cancer | mirror filename only | explicit | `MIRROR_FILENAME_ERROR`, frozen |
| R1 | explicit title/body | none found | explicit | post-hoc corroboration only |
| R2 | explicit title/body | none found | explicit | post-hoc corroboration only |
| R3 | explicit title/body | none found | explicit | post-hoc corroboration only |
| R4 | explicit title/body | none found | explicit | post-hoc corroboration only |
| R5 | explicit title/body; title visually verified | none found | explicit | post-hoc corroboration only |

All five papers describe an anti-breast-cancer/ERα task. This is `REFERENCE_CONSENSUS`, not independent provenance for the frozen source files. It cannot rewrite the already established `MIRROR_FILENAME_ERROR` classification.

## Target and entity semantics

- The papers model pIC50 and predict the same conceptual five ADMET endpoints.
- None documents a three-workbook key join with the row-level rigor of `run-001`. Workflows generally drop identifier columns and proceed by row alignment; this is a provenance weakness when independently reproducing the analysis.
- The frozen run verifies exact entity alignment, preserves source hashes and row identities, and separates source facts from assumptions.
- No reference supplies official wording or external pharmacology evidence that resolves the favorable CYP3A4 label. Their disagreement reinforces the frozen ambiguity treatment.

## Decision

Reference agreement supports the plausibility of the frozen interpretation but has no authority to alter it. Source/entity provenance remains a `STRONG` capability of the current run and Skill workflow.
