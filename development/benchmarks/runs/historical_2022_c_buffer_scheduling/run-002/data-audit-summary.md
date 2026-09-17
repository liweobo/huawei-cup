# Data Audit Summary

## Canonical Summary

| Workbook | Sheet | Dimensions | Data rows | Columns | Missing | Duplicate full rows |
|---|---|---:|---:|---|---:|---:|
| attachment1.xlsx | Sheet1 | A1:D319 | 318 | 4 | 0 | 0 |
| attachment2.xlsx | Sheet1 | A1:D319 | 318 | 4 | 0 | 0 |
| attachment3.xlsx | Sheet1 | A1:B75 | 74 | 2 | 0 | 0 |
| attachment4.xlsx | Sheet1 | A1:CX51 | 50 template rows | 102 | 0 | 0 |

All four files were read with `openpyxl` in read-only data mode. The two
vehicle workbooks have headers `进车顺序, 车型, 动力, 驱动`; their IDs are
unique and exactly `1..318`.

## Data To Problem Mapping

| Data field / artifact | Meaning | Problem role | Unit / domain | Risk |
|---|---|---|---|---|
| `进车顺序` | painting-output source order | input sequence | integer | None observed |
| `车型` | model class | descriptive | `A` or `B` | not part of stated score |
| `动力` | powertrain | objective 1 | `混动` or `燃油` | source-order frequency is uneven |
| `驱动` | drive type | objective 2 | `两驱` or `四驱` | block definition is ambiguous |
| Attachment 3 region code | PBS area / position | output matrix vocabulary | integer codes 0-3, 71-710, 11-610 | codes must match exactly |
| Attachment 4 | 50 x 100 template | output layout example | blank cells | not a solution |

## Observed Distributions

Attachment 1:

- 318 vehicles;
- model A/B counts: 264 / 54;
- hybrid/fuel counts: 212 / 106;
- 4WD/2WD counts: 29 / 289.

Attachment 2:

- 318 vehicles;
- model A/B counts: 264 / 54;
- hybrid/fuel counts: 159 / 159;
- 4WD/2WD counts: 29 / 289.

The changed hybrid/fuel balance in Attachment 2 is consistent with the
statement that it was adjusted to test adaptability.

## Cross-Attachment Consistency

- Attachment 1 and Attachment 2 have the same four-column header and the
  same 318 unique source IDs.
- Attachment 3 has 74 entries: 60 inbound positions (`11` through `610`),
  10 return positions (`71` through `710`), and four fixed regions
  (`0`, `1`, `2`, `3`).
- Attachment 4 has a time header `0..100`, 50 vehicle rows, and blank cells.
  It is a template only and is not used as real input.
- The statement and workbook fields agree on the region-code vocabulary.

## Audit Limitations

- The GitHub directory is an accepted historical mirror, not an independently
  verified competition-organiser host.
- The statement does not define a unique second-by-second semantics for
  zero-time load/unload overlap; the adopted interpretation is recorded in
  `problem-facts.md`.
- No outlier deletion, imputation or label rewriting was performed.
