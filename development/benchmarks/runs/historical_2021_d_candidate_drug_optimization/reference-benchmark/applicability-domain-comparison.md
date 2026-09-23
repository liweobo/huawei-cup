# Applicability-Domain Comparison

## Evidence by solution

| solution | marginal range | distance/leverage/neighbor/density | predictive uncertainty | molecular feasibility | assessment |
|---|---|---|---|---|---|
| Frozen `run-001` | finite source rows | target-specific empirical support gates, including train-distribution distance checks | activity fold SD in objective | real provided compounds, but no experimental proof | bounded empirical applicability domain |
| R1 | min/max bounds | none | none | unverified continuous vector | `SURROGATE_EXTRAPOLATION_UNVERIFIED` |
| R2 | min/max bounds | none | none | unverified continuous vector | same |
| R3 | min/max bounds | none | optimizer-repeat dispersion only | unverified; limitation acknowledged | same |
| R4 | min/max/range reporting | none | none | unverified continuous vector | same |
| R5 | min/max plus four integer restrictions | none | none | unverified continuous vector | same |

Marginal min/max bounds do not establish joint support. A vector may be inside every univariate range while lying far from all training compounds or violating descriptor relationships.

## Gap gate: `PREDICTIVE_SURROGATE_APPLICABILITY_DOMAIN_CONTRACT`

| required condition | result | evidence |
|---|---|---|
| 1. current Skill lacks the capability | `FAIL` | the Skill has general validation, feasibility, evidence, and claim-boundary rules; dedicated predictive-surrogate AD wording is only partial/terse |
| 2. run-001 made or nearly made a material error because of it | `FAIL` | run-001 applies target-specific empirical applicability gates before ranking |
| 3. the run-local prompt did not supply an adequate guard | `FAIL` | the benchmark contract explicitly required applicability checks and the run implemented them |
| 4. references/strong method evidence reveal the missing guard | `FAIL` | all five references omit a meaningful AD check; they illustrate the risk but do not provide a stronger general contract |
| 5. capability generalizes across drug problems | pass | predictive-surrogate domains recur broadly |
| 6. capability applies to materials/formulations/engineering | pass | the same extrapolation issue recurs |
| 7. capability can change correctness | pass in principle | unsupported extrapolation can invalidate a decision, but did not here |
| 8. lightweight implementation is possible | pass | train-support distance and range gates are feasible |
| 9. testable | pass | synthetic in/out-of-domain cases can be checked |
| 10. scope remains bounded | pass | a compact contract need not become AutoML |

Four necessary conditions fail. The candidate does not qualify as `G1`. The correct classification is a `P2` documentation weakness: the general Skill guidance could be more explicit, while the frozen run is already correct.

## Level

`APPLICABILITY_DOMAIN: ADEQUATE` at the reusable Skill level and strong in this run. This rating does not change the graduation verdict.
