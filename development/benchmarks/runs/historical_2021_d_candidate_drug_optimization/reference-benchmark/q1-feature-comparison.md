# Q1 Descriptor and Feature Comparison

## Screening pipelines

| solution | initial descriptors | preprocessing and screening | final activity set | selection scope | stability evidence |
|---|---:|---|---:|---|---|
| Frozen `run-001` | 729 | fold-local near-constant, exact-duplicate, and correlation audit; fold-local F-regression ranking | 20 | `TRAIN_FOLD_LOCAL` | mean pairwise Jaccard `0.812`, range `0.739–0.905` |
| R1 | 729 | remove 344 mostly-zero and 26 anomaly-heavy columns; RF/entropy top 30; Pearson redundancy | 20 | `FULL_DATA` | single Top-N only |
| R2 | 729 | LASSO/Pearson/RF/MI top-40 vote; distance correlation | 20 | `FULL_DATA` | method agreement only; no resampling stability |
| R3 | 729 | remove 225 constants; GRA to 200; 50 RF-RFE repeats plus 10 RF-importance repeats | 20 | `FULL_DATA` | perturbation/repeat frequency, but outside a held-out fold |
| R4 | 729 | remove 270 rare columns; Spearman removes 213 redundant and 50 weak columns; RF/permutation/SHAP | 20 reported from a 196-column pool | `FULL_DATA` and test-informed importance | no fold/bootstrap stability |
| R5 | 729 | GRA to 70; distance correlation to 37; RF ranking | 20 | `FULL_DATA` | single Top-N only |

## Leakage assessment

All five references use outcome information to choose activity descriptors before the reported split or CV. Their downstream CV therefore evaluates a feature set already informed by validation rows. This is `REFERENCE_FEATURE_SELECTION_LEAKAGE_RISK`; R4 additionally uses test-set permutation importance. The frozen run's selection operation is fitted separately within every outer training fold, so its outer metrics remain out-of-sample with respect to feature choice.

R3 is the only reference with meaningful repeated-selection evidence. Its 50 RF-RFE and 10 importance repetitions reduce single-fit instability, but they do not replace nested/fold-local evaluation because the repeated procedures still see the full labeled dataset.

## Correlation, constants, and dimension

- All solutions recognize high dimension and reduce 729 inputs to a small activity set.
- R1, R3, and R4 explicitly remove degenerate or sparse columns. R2 and R5 rely more heavily on supervised/dependence screens.
- R1, R2, R3, and R4 include some redundancy/dependence filtering. The frozen run also audits exact duplicates and applies filtering inside each training fold.
- None of the references uses PCA as the final activity representation.

## Importance and claim boundary

The reference papers commonly describe selected variables as having a “significant influence” on activity. Their procedures establish predictive association or model importance; they do not identify biological mechanism or causality. The frozen run states this boundary explicitly. No reference supplies experimental intervention evidence that would justify upgrading importance to mechanism.

## Finding

The references add useful algorithm examples, especially R2's method voting and R3's repeated selection. They do not reveal a missing general feature-discipline capability. The frozen run is stronger on fold safety and quantified stability; algorithm choice and exact selected variables are `G3 REFERENCE DIFFERENCE` or `G5 ALGORITHM / SEARCH QUALITY`.
