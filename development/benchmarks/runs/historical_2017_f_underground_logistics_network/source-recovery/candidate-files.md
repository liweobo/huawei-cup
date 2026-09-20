# Candidate Files And Copy Comparison

One institutional archive, C01, was downloaded. It contains a ZIP and a separate map; the ZIP contains only the original DOC and an XLS. Member names were listed before extraction. No solution-like member was present. Detailed file metadata and SHA256 values are in [attachment-manifest.json](attachment-manifest.json).

## Internal Evidence

| File | Evidence |
|---|---|
| F.rar | RAR signature; HTTP 200 and advertised length match 2,897,538 downloaded bytes; `tar` extraction succeeded |
| 2017年中国研究生数学建模竞赛F题.zip | ZIP signature; both member CRCs verified by `ZipFile.testzip()` and reads |
| Original DOC | 2,579,456 bytes; same SHA256 and Git blob as frozen run-001; ZIP member date 2017-09-13 15:26:12, timezone unspecified |
| XLS | BIFF8 inside OLE; two visible worksheets; ZIP member date 2017-09-13 14:47:52, timezone unspecified |
| JPG | 2780 x 1579 RGB JPEG; 144 DPI is file metadata, not a map scale; visually reviewed full image and native-resolution crops |

XLS OLE metadata reports Microsoft Excel, creation time `2017-07-05 02:56:18`, last-save time `2017-09-13 03:32:39`, author `dell`, last saved by `AutoBVT`. These are recorded as internal metadata, not proof of authorship or authenticity. They do not establish a timezone. The only OLE streams are Workbook and two summary-information streams. No embedded paper or additional data file was found there.

## Structural Comparison

| Item | Shape / labels / units |
|---|---|
| 现状全天OD | A1:DK115, including headers; 114 x 114 data block B2:DK115 |
| OD labels | 1, 2, 3, 4, followed by 791 through 900, identically ordered on both axes |
| OD units | Tonnes from original DOC; full-day basis from worksheet title; horizontal-axis origin to vertical-axis destination from DOC |
| 各区域中心点及面积 | Populated A1:F115; xlrd reports two additional formatted-empty columns G:H |
| Attribute labels | Same 114 ordered IDs as OD; 114 coordinate pairs in metres |
| Region attributes | 110 regions, 791-900, with areas in km^2 and m^2 and traffic congestion indices |
| Four separate points | IDs 1-4 have coordinates and OD keys; area/index fields are blank; four matching blue map labels |

## Equivalence Decisions

- C01-DOC versus frozen original DOC: `IDENTICAL_COPY`. Same filename semantics, size, SHA256, and Git blob; no text-only comparison substituted for byte verification.
- C01-XLS and C01-MAP: one original-file mirror candidate each. No independent second copy acquired, so no claim of `IDENTICAL_COPY` or `SEMANTICALLY_EQUIVALENT_COPY` across attachment mirrors.
- Two independent XLS parser outputs: identical cell values over 14,145 compared cell positions after padding Calamine's omitted empty columns. This is parser verification, not an independent provenance source.
- `CONFLICTING_COPY`: none observed within the material inspected. This is not proof that no conflicting version exists elsewhere.
- `UNVERIFIED_COPY`: no alternate attachment copy adopted. The accepted mirror still lacks organizer signature/archival authentication, explicitly retained as a provenance limitation.

No original numerical data were edited. In particular, the two nonzero diagonal OD entries (895: 2.92; 896: 0.52), congestion values above 10, and blank park attributes remain intact. These are future input-audit considerations, not grounds to invent a replacement attachment.
