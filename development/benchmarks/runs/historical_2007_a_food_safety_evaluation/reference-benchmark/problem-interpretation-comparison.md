# Problem Interpretation Comparison

## Formal target extracted from the problem and references

The shared core is statistical dietary-exposure risk modeling, not a generic multi-criteria alternatives-ranking task. Every unique reference models food intake and contaminant concentration, derives an absolute exposure distribution, estimates its `99.999%` right quantile, and relates that physical quantity to a safety standard. The problem does not require a ranking of regions, foods, or candidate assurance systems.

| reference | evaluation object | decision question | target types | ranking required/added | object drift |
|---|---|---|---|---|---|
| `REF-01` | region-season-population contaminant intake; numerical example uses Beijing Dongcheng lead | which regions need warning, and is exposure acceptable? | A, B, C, D, H | not required; high-PI-region triage added | yes: daily intake is later compared with blood-lead concentration |
| `REF-02` | population/region/food-contaminant exposure | does `Q_0.99999` exceed a daily intake warning standard? | A, B, C, H | no | no major drift; standard remains unspecified |
| `REF-03` | population-region daily contaminant intake | is the absolute tail below an authority standard? | A, B, C, H | no | no |
| `REF-04` | age-group/region/food-contaminant intake | is the tail below an age/body-weight-compatible toxicological threshold? | A, B, C, H | no | no; it explicitly critiques an unstratified target |
| `REF-05` | region-season-food-contaminant daily intake | is the tail safe, and can the result support a national database? | A, B, C, H | no | yes: daily intake becomes food-content compliance, then national safety |
| `REF-06` | same as `REF-02` | same as `REF-02` | A, B, C, H | no | duplicate |

Target codes: A `ABSOLUTE_EXPOSURE_DISTRIBUTION`; B `EXTREME_QUANTILE`; C `REGULATORY_COMPLIANCE`; D `ABSOLUTE_RISK_PROBABILITY`; E `RELATIVE_COMPOSITE_SCORE`; F `RANKING`; G `CLASSIFICATION`; H `MIXED`; I `UNSPECIFIED`.

No reference uses E as the principal output. G occurs only as a threshold-derived safe/warning decision, not as an independently trained classifier or an arbitrary high/medium/low rubric. Formal F is absent. `REF-01`'s screening of high exceedance-probability regions is `REFERENCE_ADDED_RANKING/TRIAGE`, not a problem requirement.

## Decision alignment

- `REF-02`, `REF-03`, and `REF-04` keep the model output and stated decision broadly aligned, subject to missing standard provenance and uncertainty.
- `REF-01` and `REF-05` change the physical meaning or scope at the decision boundary; their “safe” conclusions do not follow from the quantities compared.
- The frozen blind run is aligned: absolute quantile and threshold class are primary, while any regional order is explicitly optional relative triage.

## Risk modeling versus evaluation modeling

The hard technical work in 2007A - sampling, censoring, distribution fitting, taxonomy reconciliation, dependence, transport, and rare-tail estimation - belongs to `STATISTICAL_RISK_MODELING` and is classified G2 or G5 in the gap audit. The transition from those model outputs to a safety/probability/compliance/rank claim is an evaluation/decision-semantics issue. The two layers must not be conflated.
