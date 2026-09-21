# External Data Ledger

## Status

`NO_EXTERNAL_DATA_USED`.

No food-safety standard, modern monitoring dataset, demographic table, paper, blog, solution, excellent-paper abstract, or 2007A-specific retrospective was accessed. The only network source was the exact user-designated problem directory and target DOC recorded in `source-provenance/source.json`.

## Operational inputs referenced by the problem but not acquired

| source | claim/input | why_needed | date/scope requirement | confidence/status |
|---|---|---|---|---|
| Responsible authority standard | contaminant intake or food concentration limit `T` | hard compliance gate | standard version, effective date, contaminant, food/population, unit | `NOT_ACQUIRED`; required before real claim |
| Total-diet/household survey | individual/household food intake by region, sex, age, season, labour intensity, and income | intake distribution | survey year, design weights, household allocation | `NOT_ACQUIRED` |
| Routine and spot monitoring | detected values, nondetects, LOD/LOQ, method, sample design | contaminant distribution | food-region-season-method and sample year | `NOT_ACQUIRED` |
| Food circulation data | flow-based reweighting/coverage | representativeness | same market/time taxonomy | `NOT_ACQUIRED` |
| Port tests and pollutant emissions | supplemental contaminant evidence | coverage and source linkage | port/industry/time scope | `NOT_ACQUIRED` |

All numerical values in `outputs/` are generated from the synthetic parameters documented in `assumptions.md` and code. They are not external facts.
