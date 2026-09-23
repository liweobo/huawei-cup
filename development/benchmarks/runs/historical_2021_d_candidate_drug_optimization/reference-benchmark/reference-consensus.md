# Reference Consensus

`total_reviewed = 5`. Counts describe the papers, not source truth.

| topic | consensus observation | appears_in_n_papers | confidence |
|---|---|---:|---|
| problem title/domain | breast cancer and ERα framing | 5 | high |
| Q1 starting dimension | 729 descriptors | 5 | high |
| Q1 final activity feature count | 20 | 5 | high |
| Q1 method | supervised/dependence/tree-based screening | 5 | high |
| fold-safe Q1 selection | present | 0 | high |
| explicit feature stability | repeated/perturbation check | 1 (R3) | high |
| Q2 winner | tree ensemble/boosting family | 5 | high |
| Q2 validation | random train/test split, often with CV tuning | 5 | high |
| explicit trivial Q2 baseline contract | present | 0 | high |
| Q3 architecture | five separate endpoint classifiers | 5 | high |
| endpoint-specific Q3 feature selection | present | 4 | medium-high |
| Q3 accuracy reported | yes | 5 | high |
| Q3 PR-AUC reported numerically | yes | 0 | high |
| Q3 calibration evidence | present | 0 | high |
| CYP3A4 favorable direction | label `1` | 3 | high |
| CYP3A4 favorable direction | label `0` | 2 | high |
| reliable CYP3A4 source/external definition | present | 0 | high |
| Q4 candidate domain | continuous descriptor vector | 5 | high |
| Q4 hard at-least-3 treatment | used directly | 3 | medium-high |
| Q4 weighted/Pareto treatment | used | 2 | medium-high |
| optimization method | population/metaheuristic search | 5 | high |
| descriptor-to-molecule mapping | provided | 0 | high |
| applicability-domain distance/leverage/density | checked | 0 | high |
| predictive uncertainty used in Q4 | used | 0 | high |
| source candidate ID as final answer | provided | 0 | high |
| exact/global optimality proof | provided | 0 | high |

## Interpretation

Strong consensus exists for a 20-feature activity model, tree ensembles, separate endpoint classifiers, and heuristic descriptor optimization. It does not establish that these choices are uniquely correct. The split CYP3A4 direction and the absence of source citations mean the frozen conditional decision is better supported than adopting either majority or minority mapping.
