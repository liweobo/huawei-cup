# Weighting and Normalization Comparison

## Weight semantics

| reference | weights actually used | source/meaning | normalized? | subjective/data-driven | MCDM importance semantics |
|---|---|---|---|---|---|
| `REF-01` | regression coefficients; cluster/regional aggregation weights; Pareto tail parameter | fitted or population aggregation; provenance incomplete | as required by model | mixed | none |
| `REF-02` | fuzzy similarity scores and normalized matching weights | author-defined `10,9,7,5,3,1,0` resemblance scale | yes for matching | subjective, no expert count/calibration | none; must not be called probability/importance |
| `REF-03` | regional mixture and importance-sampling weights | target-population mixture / `p(x)/q(x)` | yes | data/model-driven | none |
| `REF-04` | demographic proportions and food-structure shares | census/sample population composition | yes | data-driven/assumed where data sparse | none |
| `REF-05` | sampling weights; rough-set-derived neural-network attribute weights; GA parameters | sampling design or predictive-model initialization | varies | data-driven plus algorithmic choices | none |
| `REF-06` | same as `REF-02` | same | same | same | duplicate |

No reference uses AHP, entropy weighting, TOPSIS, PCA-as-score, or a weighted-sum multi-criteria safety index. There is therefore no entropy-importance misuse, AHP consistency issue, or double criterion weighting to audit in the reference set.

## Normalization

| reference | normalization/transformation | range source | candidate-set dependence | absolute-risk interpretation risk |
|---|---|---|---|---|
| `REF-01` | physical-unit multiplication; fitted distributions; direct threshold comparison | physical data/threshold | no | high only because incompatible output and comparator are compared |
| `REF-02/06` | density normalization; normalized fuzzy matching weights | distribution support and matching candidates | matching weights depend on available analogues; final q does not | fuzzy coefficients could be overinterpreted, but paper keeps them as matching weights |
| `REF-03` | density normalization and importance weights | chosen proposal/target density | no alternative-ranking set | no relative score |
| `REF-04` | probability densities plus body-weight/time conversion | fixed toxicological threshold | no | low for displayed unit conversion |
| `REF-05` | fitted polynomial density/CDF; model preprocessing | fitted sample | no candidate ranking | high because absolute compliance is claimed from a mismatched threshold |

## Direction audit

All papers treat larger contaminant intake as worse and a larger safety margin below the limit as better. No benefit/cost sign reversal was found. The main defect is not direction or scale invariance; it is output/comparator semantics.

## Relation to frozen Skill

Weight provenance, units, normalization, hard constraints, equal-weight baseline, sensitivity, redundancy, and rank-reversal checks are already present in the Skill's evaluation guidance. They are `ALREADY_PRESENT`, not post-hoc gap candidates.
