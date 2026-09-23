# Q2 Activity Modeling Comparison

## Target semantics

All six solutions model `pIC50` as the activity target and use the source's 50 prediction rows for final prediction. The papers discuss IC50/pIC50 conversion with varying detail; none provides a different target definition that permits ignoring protocol differences. The frozen run preserves both target semantics and prediction-row provenance.

## Models and reported performance

| solution | selected model | reported performance | principal validation issue |
|---|---|---|---|
| Frozen `run-001` | Extra Trees | outer MAE `0.538±0.043`; RMSE `0.738±0.046`; R² `0.729±0.035` | none found; fold-local selection and frozen model family |
| R1 | random forest | test MAE `0.5511`; RMSE `0.7412`; R² `0.7367` | activity features selected on all labels before split/CV |
| R2 | HGBRT | test MSE `0.463910`; MAE `0.490858`; RMSE `0.681109`; R² `0.7811827` | full-data selection and test behavior used in model/parameter decisions |
| R3 | GBRT | test MSE `0.4376`; MAE `0.4704`; R² `0.8076` | full-data selection; tuning independence not established |
| R4 | LightGBM | MSE `0.4424` | test-set permutation importance and all-data SHAP influence the retained set |
| R5 | XGBoost | R² `0.7821` | feature selection precedes CV; main comparison omits error-scale metrics |

## Baselines

The frozen run evaluates a mean baseline under the same folds and metrics. None of R1, R2, R3, or R5 defines a trivial mean/median or regularized-linear baseline under the final protocol. R4 includes linear regression among a large candidate menu, but does not establish it as a frozen baseline contract and then uses the held-out test set during feature selection. Large model menus do not replace a same-split baseline.

## Model complexity

The reference winners span RF, histogram gradient boosting, GBRT, LightGBM, and XGBoost. Their higher single-split R² values do not establish a Skill gap: tree-boosting choice is an algorithm-quality difference, while the comparison protocols contain selection leakage or incomplete independence. Extra Trees is a defensible winner under the frozen run's outer protocol.

## Prediction scope and uncertainty

The frozen run retains outer-fold prediction standard deviations for the 50 source candidates. None of the references propagates predictive variance or ensemble disagreement into Q4. R3 repeats its optimizer, which measures search variability rather than predictive uncertainty.

## Finding

The frozen and reference Q2 numbers are `NOT_DIRECTLY_COMPARABLE`. No paper matches all of: training rows, fold-local feature selection, model-family freeze, split membership, metric aggregation, and uncertainty protocol. The references demonstrate alternative algorithms, not a correctness failure in the frozen solution.
