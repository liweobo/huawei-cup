# Independent Original Input Audit

Status: PASS for the recovered essential source set. Native XLS cell equality
between xlrd and python-calamine is exact; no missing or negative/nonfinite OD.
DOC and JPG were separately rendered/viewed, not inferred from prior solutions.

| Item | Observed |
| --- | --- |
| OD | 114 x 114; IDs1-4 and791-900 |
| Convention | Column origin, row destination |
| Asymmetric unordered pairs | 5607 |
| Total tonne/day | 163406.46000000002 |
| Park-related tonne/day | 128865.538 |
| Diagonal | 895:2.92;896:0.52 tonne/day, preserved |
| Region congestion range | [1.33, 11.54] |
| Blank park attributes | 12 cells across two area units and congestion; no imputation |
| Coordinates | metres; CRS/origin/projection not given |

Region areas are retained but not required for the explicit centre-coverage
approximation. Covering a centre does not assert whole-polygon coverage.
Uncalibrated map pixels are not metric inputs. Original sheets, IDs, source
cells and units remain in source-manifest.json, node-ledger.md, demand-ledger.md
and inputs/*.csv. See results/input-audit.json for machine checks.
