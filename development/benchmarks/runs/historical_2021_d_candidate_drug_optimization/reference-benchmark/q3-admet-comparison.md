# Q3 ADMET Classification Comparison

## Endpoint models and metrics

| solution | feature policy | selected model families | primary reported evidence | threshold | calibration |
|---|---|---|---|---|---|
| Frozen `run-001` | endpoint-specific, fold-safe | five independently selected binary pipelines | PR-AUC `0.801–0.991`, ROC-AUC, balanced accuracy, minority metrics, prevalence, fold dispersion | validation-only, frozen before test | Brier and calibration diagnostics |
| R1 | one common 359-feature set for all endpoints | RF for all five | ROC-AUC and accuracy | default/unstated | absent |
| R2 | endpoint-specific | HGB classifiers | accuracy (`0.88–0.97`) | default; penalty parameter chosen with test accuracy | absent |
| R3 | endpoint-specific | SVM for three, XGBoost for two | accuracy (`90.88%–96.96%`) | default/unstated | absent |
| R4 | endpoint-specific WOE/IV | XGBoost for three, RF for two | accuracy, precision, recall, F1, ROC, PR curves, log loss | default/unstated | absent |
| R5 | endpoint-specific RF+GA | RF/XGBoost | accuracy (`0.8684–0.9636`) and ROC curves | rounding/default `0.5` | absent |

## Imbalance discipline

- R1 acknowledges imbalance but prefers ROC/accuracy and explicitly omits PR-based selection.
- R2 and R3 primarily select by accuracy; neither gives prevalence-relative PR-AUC, balanced accuracy, or a majority baseline.
- R4 reports the broadest metric set and includes PR curves, but the reported workflow applies SMOTE before the holdout split, so synthetic-neighbor information may cross the evaluation boundary.
- R5 relies on accuracy and ROC plots without a prevalence or calibration account.
- The frozen run reports endpoint prevalence, a majority baseline, PR-AUC, minority-class behavior, balanced metrics, and fold variation.

## Threshold and leakage findings

No reference documents validation-only threshold selection. R2 uses test accuracy while adjusting a classifier penalty, and R4's reported order places SMOTE before the split. Full-data supervised feature selection is also present in the reference pipelines. These issues prevent reference accuracies from acting as clean benchmarks for the frozen run.

## Endpoint semantics

All papers build five separate classifiers for Caco-2, CYP3A4, hERG, HOB, and MN. Their Q4 desirability mappings agree on Caco-2=`1`, hERG=`0`, HOB=`1`, and MN=`0`, but they split on CYP3A4. The CYP3A4 evidence is analyzed separately in [cyp3a4-semantics-comparison.md](cyp3a4-semantics-comparison.md).

## Cross-target reuse

R1 forces a common 359-feature pool across all endpoints without comparative evidence, so `CROSS_TARGET_FEATURE_REUSE_UNJUSTIFIED` applies. R2–R5 use endpoint-specific selections, aligning with the frozen run's principle, but their selection operations are not kept inside evaluation folds.

## Finding

The reference model families and reported accuracies are useful algorithm examples. The frozen run is materially stronger on imbalance-aware evaluation, threshold provenance, calibration, fold safety, and retained decision evidence. No missing P0/P1 classification capability is revealed.
