# Q4 Optimization Comparison

## Optimization objects and rules

| solution | candidate domain | ADMET rule | objective | search | reported output |
|---|---|---|---|---|---|
| Frozen `run-001` | fixed 50 real source compounds | hard: finite descriptors, at least 3 favorable endpoints, all target-specific applicability gates | predicted activity minus 1 outer-fold prediction SD | exhaustive enumeration | conditional `TEST026`; reversed-CYP `TEST019`; unconditional recommendation withheld |
| R1 | continuous 20-descriptor vector | `HARD_K_OF_5` | maximize predicted pIC50 | GA | descriptor ranges |
| R2 | continuous 20-descriptor vector | manually weighted endpoint score in a scalarized/multiobjective formulation | activity/ADMET weighted score, assumed λ=`0.5` | NSGA-III | pIC50 `10.098`, pattern `10011` |
| R3 | continuous 56-descriptor vector | `HARD_K_OF_5` | maximize predicted pIC50 | differential evolution | descriptor vector, pIC50 about `9.5325` |
| R4 | continuous 196-descriptor vector | Pareto/primary-target treatment | predicted activity and encoded ADMET behavior | multiobjective PSO | descriptor ranges |
| R5 | continuous 70-descriptor vector | reward constrained to 3–5 favorable endpoints | predicted activity and ADMET reward | GA compared with SA/artificial fish | descriptor solution, claimed `4.3%` improvement |

## Descriptor feasibility

Every reference edits molecular descriptors as independent decision variables and constrains them mainly by marginal training ranges. None maps the resulting vector to a valid molecular graph, checks chemical consistency among descriptors, proves synthesizability, or identifies one of the 50 provided candidate compounds. Therefore all five receive `DESCRIPTOR_FEASIBILITY_UNVERIFIED`.

R3 explicitly acknowledges that descriptors may not vary independently, which improves its claim boundary. R5 adds four integer restrictions, but that does not establish joint chemical realizability. A larger continuous search space is not automatically more valid than the frozen run's finite source-candidate domain.

## ADMET combination

R1, R3, and R5 impose a version of the stated “at least three favorable properties” rule. R2 uses a manually constructed score and an assumed activity weight; its result can change with arbitrary scalarization. R4 uses multiobjective/primary-target analysis but does not establish a source-derived probability or utility model. None of the weighted/reference scores is a validated “overall ADMET probability.”

## Baseline and status

No reference compares its final continuous descriptor result with the best feasible observed/source compound under the identical decision rule. R1, R2, R4, and R5 use language that can be read as an optimum without exact proof; they support only `HEURISTIC_BEST_FOUND`. R3 explicitly describes its result as locally/budget limited. The frozen run enumerates all 50 allowed candidates, so its optimum is exact for the declared finite domain while retaining the surrogate label.

## TEST026 and TEST019

No reference selects a source candidate ID, so none selects or contradicts `TEST026` or `TEST019`. Descriptor-vector outputs cannot be compared to those IDs until a valid molecule mapping, matching desirability rule, and matching applicability policy exist.

## Finding

The references explore broader chemistry-specific search ideas but do not show a general integration gap. Their main differences are candidate-domain assumptions (`G3`), heuristic/model choices (`G5`), chemistry-specific realizability (`G2`), and reference weaknesses (`G4`). The frozen run provides the strongest auditable answer to the stated finite-candidate decision problem.
