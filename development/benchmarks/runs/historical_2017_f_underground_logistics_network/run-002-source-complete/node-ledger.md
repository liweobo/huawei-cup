# Node Ledger

| Node ID | Meaning / type | Position provenance | Status |
|---|---|---|---|
| 791-900 | Original freight regions, not automatically stations | XLS `各区域中心点及面积` A6:A115, D6:E115; original map red labels | GIVEN |
| 1-4 / K1-K4 | Four external logistics parks | XLS A2:A5,D2:E5; blue map markers and DOC four-park statement | SOURCE_CROSS_REFERENCE_INFERENCE |
| S000... | Constructed secondary service stations | Original centre seed plus disclosed overflow offset; source_seed_id and served_regions stored | ASSUMED design variables |
| P000... | Constructed primary interchanges | Corresponding secondary position plus disclosed north offset | ASSUMED design variables |

Source coordinates, area, congestion and exact source rows are retained in `inputs/locations.csv`. Blank park attributes are not copied into ordinary region calculations. Original IDs are categorical identifiers, not metric coordinates or ordinal labels.

`results/<name>/node-results.json` gives every actual constructed node's location, own primary, covered region fractions, radius, ground freight, directed underground inflow/outflow and departures. Multiple stations serving one original region do not duplicate its demand. Source regions are representative points; intra-zone polygon geometry and unmeasured travel are not recovered by aggregation.

A primary with no nearest-park association has an explicit undefined/NOT_APPLICABLE source transfer-ratio denominator. All primaries receive a row in `transfer-ratios.json`; park-specific ratios are never arbitrarily pooled across parks.
