# 2021D Reference Source Ledger

## Scope and handling

- Reference repository: <https://github.com/zhanwen/MathModel/tree/master/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2021%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/D>
- Review mode: post-hoc comparison only; no reference is treated as ground truth.
- Coverage: all 291 pages across the five listed PDFs were text-reviewed, with rendered-page checks for titles, method diagrams, metric tables, optimization results, and conclusions.
- Identity check: every downloaded byte stream reproduced the user-supplied Git blob ID. SHA256 values below identify the reviewed bytes.
- Award rule: no reliable official award evidence was located in the supplied source set. Every award is therefore `UNKNOWN`; filenames, institutions, page counts, and layout were not used to infer an award.
- Confidence vocabulary: `HIGH` means the paper states the item in text/table/code; `MEDIUM` means the workflow is recoverable but a detail is implicit or internally inconsistent.

## Identity summary

| reference_id | filename | git_blob | sha256 | pages | title | authors | institution | award_level | award_verified |
|---|---|---|---|---:|---|---|---|---|---|
| R1 | `D21101080006.pdf` | `578f9f8a3b3f030bd0b4e7b8456627d0eadbd045` | `f9ac7ba22b06ee6d84a6f10b32a8b973c99feb57d789069b9018cf6835fbbf76` | 65 | 抗乳腺癌候选药物的优化建模 | 祝海峰、陈庆辉、孟颖岫 | 山西大学 | `UNKNOWN` | `false` |
| R2 | `D21102700119.pdf` | `731850f70e41f036e2edfe53f206c2dfc8873779` | `0355de2dacb187522ace7c5d858d6db08427d693f9a42319a794ab8f5757f391` | 49 | 基于数据挖掘的抗乳腺癌候选药物的优化模型 | 陆悦、熊斯洁、施晨扬 | 上海师范大学 | `UNKNOWN` | `false` |
| R3 | `D21102980066.pdf` | `7f000f3664b534cde53be98fbcbf3f842683693d` | `030d464446526c366370b53b90058dd6d69cd43f9e9250e8f4bf8f1a6e9a1bcc` | 53 | 抗乳腺癌候选药物的优化建模 | 钱伟杰、石泽峰、王汉钊 | 南京林业大学 | `UNKNOWN` | `false` |
| R4 | `D21104860088.pdf` | `c33f967f2510a8202e400fb3f630d9f06936a61e` | `6adc2185fdcee00276ce0b4e61bbe4bb5c97cb1cec579d9cc33c199d1715a8b0` | 69 | 抗乳腺癌候选药物的优化建模 | 陈苗苗、孙冉、王继莲 | 武汉大学 | `UNKNOWN` | `false` |
| R5 | `D21116460003.pdf` | `aece8efce5d3e7ab22d74c851b3ecc754b017fe9` | `322ec9baf97abad7f1db721b48bc2bc9eb2aacb85d87718a6b8550f893f9c246` | 55 | 抗乳腺癌候选药物的优化建模 | 赵禹萌、马涛、叶建明 | 宁波大学 | `UNKNOWN` | `false` |

## R1 — D21101080006

- `Q1_method`: start from 729 descriptors; remove 344 columns with more than 90% zeros and 26 anomaly-heavy columns; compare random-forest importance with entropy weights; retain the RF top 30; remove highly Pearson-correlated variables; finish with 20.
- `Q2_method`: use the Q1 20 descriptors; compare SVR, neural network, GBRT, and random forest with an 80/20 random split and random-search/5-fold tuning; select random forest.
- `Q3_method`: use the common 359 preprocessed descriptors for five separate SVM/SGD/DNN/RF endpoint models; select RF for all five using ROC-AUC and accuracy.
- `Q4_method`: optimize a continuous 20-descriptor vector within observed marginal ranges; require at least three favorable endpoint classes; maximize predicted pIC50 with a genetic algorithm.
- `feature_selection_method`: RF/entropy ranking plus Pearson redundancy filtering.
- `activity_model`: random forest; test RMSE `0.7412`, MAE `0.5511`, R² `0.7367`.
- `ADMET_models`: five random forests; reported test ROC-AUC `0.9069–0.9803`, accuracy `0.8201–0.9218`.
- `candidate_generation`: continuous descriptor editing; no molecular structure reconstruction.
- `optimization_method`: genetic algorithm; `HEURISTIC_BEST_FOUND` under the reported evidence.
- `validation_protocol`: `TRAIN_TEST_SPLIT` plus CV-based tuning, but Q1 selection was performed on all 1,974 labeled rows before the split/CV (`FULL_DATA`; `REFERENCE_FEATURE_SELECTION_LEAKAGE_RISK`).
- `reported_metrics`: Q2 MAE/RMSE/R²; Q3 ROC-AUC/accuracy; no trivial regression baseline, PR-AUC, calibration, Q4 prediction uncertainty, or applicability-domain distance.
- `final_candidate`: descriptor ranges rather than a source candidate ID; no `TEST026`/`TEST019` selection.
- `claim_scope`: optimization of predicted descriptors/pIC50; wording about optimization effects is stronger than the unverified descriptor-to-molecule feasibility supports.
- `confidence`: `HIGH`.

## R2 — D21102700119

- `Q1_method`: obtain top-40 lists from LASSO, Pearson, random forest, and mutual information; vote across lists; use distance correlation to finish with 20 descriptors.
- `Q2_method`: compare eight regressors under an 80/20 random split and K-fold training; select histogram gradient boosting regression.
- `Q3_method`: construct endpoint-specific feature sets and histogram gradient boosting classifiers with class weighting/penalty.
- `Q4_method`: optimize a continuous 20-descriptor vector with an activity/ADMET scalarization described as NSGA-III; use a manually encoded five-endpoint score and assumed activity weight `0.5`.
- `feature_selection_method`: multi-method vote plus distance-correlation filtering.
- `activity_model`: HGBRT; test MSE `0.463910`, MAE `0.490858`, RMSE `0.681109`, R² `0.7811827`.
- `ADMET_models`: endpoint-specific HGB classifiers; reported accuracies approximately `0.88–0.97`.
- `candidate_generation`: continuous descriptor editing; no molecular structure reconstruction.
- `optimization_method`: NSGA-III/scalarized multiobjective heuristic; weight sensitivity is shown, but the score provenance remains assumed.
- `validation_protocol`: `TRAIN_TEST_SPLIT` plus K-fold work; full-data feature selection precedes CV, and test accuracy/test behavior is used in model/parameter decisions (`REFERENCE_DATA_LEAKAGE`).
- `reported_metrics`: Q2 MSE/MAE/RMSE/R²; Q3 accuracy; no trivial regression baseline, imbalance metric set, calibration, Q4 prediction uncertainty, or applicability-domain check.
- `final_candidate`: continuous descriptor vector with predicted pIC50 `10.098` and reported ADMET pattern `10011`; no source candidate ID.
- `claim_scope`: model-predicted optimum; arbitrary scalarization and unrealized descriptor vector weaken physical and probability semantics.
- `confidence`: `HIGH` for the reported workflow and metrics; `MEDIUM` for the intended multiobjective semantics.

## R3 — D21102980066

- `Q1_method`: remove 225 constant descriptors; grey-relation screen to 200; repeat RF-RFE 50 times and random-forest importance 10 times; combine frequency/importance checks to obtain 20.
- `Q2_method`: reduce the Q1 set to 19 after distance-correlation redundancy filtering; compare SVR, RF, GBRT, XGBoost, and BP network on an 80/20 random split; select GBRT.
- `Q3_method`: build endpoint-specific MIC/RFE feature sets; compare SVM, RF, and XGBoost families; choose SVM for Caco-2/CYP3A4/hERG and XGBoost for HOB/MN.
- `Q4_method`: optimize a continuous 56-descriptor union within marginal min/max bounds, require at least three favorable endpoints, and maximize predicted pIC50 using differential evolution.
- `feature_selection_method`: constant removal, GRA, repeated RF-RFE/frequency, RF importance, and dependence checks.
- `activity_model`: GBRT; test MSE `0.4376`, MAE `0.4704`, R² `0.8076`.
- `ADMET_models`: SVM/XGBoost by endpoint; reported accuracy `90.88%–96.96%`.
- `candidate_generation`: continuous descriptor editing; the authors explicitly note that independent descriptor variation may be unrealistic.
- `optimization_method`: differential evolution; eight repeats are discussed and the paper appropriately acknowledges a local/best-found status.
- `validation_protocol`: `TRAIN_TEST_SPLIT`; supervised feature selection uses the full labeled data before the split/CV (`FULL_DATA`; leakage risk); tuning independence is not established.
- `reported_metrics`: Q2 MSE/MAE/R²; Q3 accuracy; no trivial regression baseline, imbalance metric set, calibration, predictive uncertainty, or applicability-domain check.
- `final_candidate`: descriptor vector with predicted pIC50 about `9.5325`; no source candidate ID.
- `claim_scope`: predicted descriptor optimum with an explicit limitation on realizability and global optimality; still no structural feasibility proof.
- `confidence`: `HIGH`.

## R4 — D21104860088

- `Q1_method`: remove 270 rare descriptors; impute anomalies; apply Spearman filtering (213 redundant and 50 weak variables removed) to retain 196; rank with RF built-in importance, permutation importance, and SHAP; report 20 important descriptors.
- `Q2_method`: compare 12 regressors and select LightGBM; appendix code uses a 75/25 split and GridSearchCV.
- `Q3_method`: use WOE/IV endpoint-specific screening, SMOTE, and a broad model comparison; select XGBoost for Caco-2/CYP3A4/hERG and random forest for HOB/MN.
- `Q4_method`: optimize a continuous 196-descriptor vector using multiobjective PSO/primary-target analysis and report descriptor ranges.
- `feature_selection_method`: Spearman filtering plus RF/permutation/SHAP ranking.
- `activity_model`: LightGBM; reported MSE `0.4424`.
- `ADMET_models`: endpoint-specific XGBoost/RF; reported accuracy `92.0%–97.8%`; also reports precision, recall, F1, ROC, PR curves, and log loss for model comparisons.
- `candidate_generation`: continuous descriptor editing; no molecular structure reconstruction.
- `optimization_method`: particle swarm multiobjective heuristic; no exact optimality proof.
- `validation_protocol`: `TRAIN_TEST_SPLIT` plus 10-fold tuning; permutation importance is evaluated on `X_test`, SHAP is used across all `X`, and the workflow places SMOTE before the split, creating test/selection and resampling leakage risks.
- `reported_metrics`: Q2 includes MSE/MAE/RMSE/R² plots; Q3 has the widest metric menu among references, but no probability calibration or validation-only threshold provenance; no Q4 predictive uncertainty/applicability domain.
- `final_candidate`: descriptor ranges, not a source candidate ID.
- `claim_scope`: predicted descriptor regions framed as drug optimization; synthesizability, efficacy, and safety remain unverified.
- `confidence`: `HIGH` for stated tables and code; `MEDIUM` where narrative and appendix protocol differ.

## R5 — D21116460003

- `Q1_method`: grey-relation screening to 70, distance-correlation screening to 37, and random-forest ranking to 20.
- `Q2_method`: compare three feature-selection routes across RF/XGBoost/GBDT/ensemble models; select MIC+RFE with XGBoost.
- `Q3_method`: use endpoint-specific RF top-60 sets followed by genetic feature selection; compare RF and XGBoost.
- `Q4_method`: define a continuous 70-descriptor union (20 activity, 55 ADMET, 5 overlaps), constrain a reward to 3–5 favorable properties, and compare genetic, simulated-annealing, and artificial-fish heuristics.
- `feature_selection_method`: GRA, distance correlation, RF; MIC+RFE for Q2; RF+GA for Q3.
- `activity_model`: XGBoost; reported R² `0.7821` for the selected MIC+RFE route.
- `ADMET_models`: RF/XGBoost; reported best accuracies `0.8684–0.9636`.
- `candidate_generation`: continuous descriptor editing with four integer restrictions; no molecular structure reconstruction.
- `optimization_method`: GA selected after heuristic comparison; the evidence supports `HEURISTIC_BEST_FOUND`, not the paper's stronger global-optimum wording.
- `validation_protocol`: `TRAIN_TEST_SPLIT` (4:1) plus K-fold evaluation, but appendix selection code fits RFE/genetic selection on all labeled rows before cross-validation (`FULL_DATA`; leakage risk).
- `reported_metrics`: Q2 R² only in the main comparison; Q3 accuracy and ROC curves; no trivial regression baseline, PR-AUC, calibration, Q4 prediction uncertainty, or applicability-domain check.
- `final_candidate`: descriptor solution and a claimed `4.3%` optimization improvement; no source candidate ID. Appendix code appears to optimize activity and ADMET descriptor blocks separately, leaving joint implementation semantics uncertain.
- `claim_scope`: predicted descriptor optimization; statements that the heuristic finds a global optimum exceed the supplied proof.
- `confidence`: `HIGH` for visually verified tables; `MEDIUM` for the Q4 joint implementation.

## Ledger conclusions

- `papers_discovered`: `5`
- `papers_fully_reviewed`: `5`
- `award_levels_verified`: `0`
- All five byte identities and page counts are internally consistent with this ledger.
- Reference weaknesses are evidence about the references, not grounds to rewrite the frozen run.
