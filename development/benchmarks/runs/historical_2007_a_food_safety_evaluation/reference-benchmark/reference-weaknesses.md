# Reference Weaknesses

The references are post-hoc comparators, not ground truth.

| reference | weakness | class | impact |
|---|---|---|---|
| `REF-01` | compares dietary intake (`µg/person-day`) with blood-lead concentration (`µg/L`) | `REFERENCE_WEAKNESS` | invalid threshold decision |
| `REF-01` | uses the quantile comparison to state lead-poisoning probability is far below `0.001%` | `REFERENCE_WEAKNESS` | unsupported probability semantics |
| `REF-01` | unversioned “international” threshold and six/four-decimal result without tail uncertainty | `REFERENCE_WEAKNESS` | false confidence |
| `REF-02/06` | exact duplicate files in source directory | `REFERENCE_SET_WEAKNESS` | naive vote counts would double one method |
| `REF-02/06` | author-created fuzzy similarity scale without expert count or calibration | `REFERENCE_WEAKNESS` | matching uncertainty hidden; not a probability |
| `REF-02/06` | unspecified warning standard and no q uncertainty/numeric real-data output | `REFERENCE_WEAKNESS` | compliance cannot be verified |
| `REF-03` | no actual monitoring data; algorithm explicitly untested | `REFERENCE_WEAKNESS` | no empirical result validation |
| `REF-03` | rare-tail sample/importance logic is described but no coverage or estimator-variance evidence is supplied | `REFERENCE_WEAKNESS` | q precision unsupported |
| `REF-04` | point-only extreme quantile under assumed lognormal/beta forms | `REFERENCE_WEAKNESS` | model/tail uncertainty ignored |
| `REF-04` | PTWI source version/date not recorded | `REFERENCE_WEAKNESS` | historical applicability incomplete |
| `REF-05` | compares daily intake q with a food-contaminant content limit and drops the denominator | `REFERENCE_WEAKNESS` | invalid regulatory-compliance claim |
| `REF-05` | polynomial “CDF” gives multiple positive roots; one is selected without monotonicity/support proof | `REFERENCE_WEAKNESS` | quantile is not uniquely established |
| `REF-05` | one region-season-food result is generalized nationally | `REFERENCE_WEAKNESS` | claim scope exceeds evidence |
| all unique works | no quantified uncertainty for `Q_0.99999` | `REFERENCE_WEAKNESS` | threshold crossing risk is undisclosed |

## Requested audits not observed

- Relative MCDM score called a probability: not observed.
- TOPSIS closeness called “percent safe”: not applicable.
- Entropy dispersion called true importance: not applicable.
- Arbitrary `0.3/0.6` safety classes: not observed.
- Fully compensatory safety total: not observed.
- Formal region/food ranking presented as a problem requirement: not observed.

Absence of those particular errors does not negate the demonstrated output-semantic failures above. It narrows the gap from a broad “evaluation framework” to a compact object/output/claim contract.
