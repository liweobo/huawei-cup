# Existing Skill Coverage

This audit distinguishes reusable Skill rules from guards added by the 2021D benchmark prompt.

| capability | coverage | existing Skill evidence | run-local contribution |
|---|---|---|---|
| feature-set design and fold-safe selection | `FULLY_PRESENT` | `references/feature-set-design.md`, `workflows/validate-model.md`, and reviewer checks require training-fold fitting and flag full-data selection | selects the concrete 20-descriptor policy and reports Jaccard stability |
| baseline and held-out regression validation | `FULLY_PRESENT` | `SKILL.md`, `rules/modeling.md`, validation/reviewer workflows require comparable baselines and generalization evidence | fixes outer protocol and model menu |
| imbalanced classification | `FULLY_PRESENT` | `references/imbalanced-classification.md` requires prevalence, majority baseline, PR-AUC, minority metrics, fold evidence, and calibration for probabilities | instantiates five endpoint-specific models |
| threshold provenance | `FULLY_PRESENT` | imbalance reference and validation workflow require validation-only threshold selection | freezes endpoint thresholds before prediction |
| evaluation semantics | `FULLY_PRESENT` | `references/evaluation-semantics.md` requires target/output/comparator/threshold provenance and allowed claims | isolates CYP3A4 ambiguity and tests both directions |
| optimization hard feasibility | `FULLY_PRESENT` | modeling rules, optimization reference, structured-improvement and reviewer rules prevent soft penalties/surrogates from overriding hard feasibility | defines finite candidate domain and target-specific AD gates |
| predictive-surrogate applicability domain | `PARTIALLY_PRESENT` | general validation, feasibility, provenance, and claim-boundary rules apply, but no dedicated compact predictive-surrogate AD contract exists | explicitly requires and implements empirical descriptor-support gates |
| uncertainty-aware decisions | `PARTIALLY_PRESENT` | validation requires robustness/uncertainty appropriate to claims; no universal prediction-SD objective is prescribed | adds `activity − 1 SD` for this decision |
| source/entity provenance | `FULLY_PRESENT` | evidence rules and workspace/run manifests require path/hash/run identity; validation checks entity units and split IDs | performs exact workbook/entity reconciliation and title audit |
| independent audit | `FULLY_PRESENT` | evidence ledger, reviewer, and final-check workflows require verifiable active artifacts and claim review | reconstructs Q4 independently |
| claim boundary | `FULLY_PRESENT` | evaluation semantics, reviewer codes, evidence rules, and best-found optimization language bound claims | states surrogate-only and withholds unconditional recommendation |
| cross-task integration | `FULLY_PRESENT` | active evidence, experiment records, feature contracts, and final checks bind artifacts and decisions across steps | links Q1/Q2/Q3 predictions to an auditable Q4 ledger |

## Assessment

The two partial rows do not establish an absent integration capability. The existing rules already require feasibility, validation, evidence scope, and bounded claims; the 2021D prompt supplies a concrete lightweight applicability implementation. The frozen reviewer correctly classifies the shorter generic wording as a P2 documentation weakness.

Recounting the fully present feature, imbalance, semantics, feasibility, provenance, reviewer, and claim rules as new gaps would be double counting.
