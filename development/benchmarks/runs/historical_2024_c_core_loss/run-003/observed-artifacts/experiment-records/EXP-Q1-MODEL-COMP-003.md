# Experiment Record

Experiment ID: EXP-Q1-MODEL-COMP-003
Problem: historical_2024_c_core_loss
Question: Q1
Purpose: Compare two genuinely different candidate classifiers against the logistic baseline.
Dataset / Version: 附件一（训练集）.xlsx; 附件二（测试集）.xlsx; run-003 immutable inputs
Feature Set: Same 26 B(t)-derived features as EXP-Q1-BASELINE-002
Models: LogisticRegression baseline; RandomForestClassifier(n_estimators=300); RBF SVC(C=10, gamma=scale)
Random Seed: 42
Split / Validation: One shared stratified random holdout, 9920 train / 2480 validation rows
Observed Metrics: All three models achieved Accuracy=1.0000, Balanced Accuracy=1.0000 and Macro F1=1.0000. Confusion matrices are identical diagonal matrices.
Attachment 2: All three models predicted the same 80 labels: 正弦波 20, 三角波 44, 梯形波 16. Pairwise disagreement count is 0 for every model pair.
Conclusion: The two candidates provide no observed gain over the baseline under this protocol. Keep the logistic model as the simplest deployable Q1 model provisionally; model selection is NOT FINAL until grouped/material-held-out validation is run.
Limitations: The single random holdout may be optimistic if similar cycles cross the split. Attachment 2 has no ground-truth waveform labels, so test accuracy is NOT OBSERVED.
Environment / Command: `python work/q1_model_comparison.py --training raw/附件一（训练集）.xlsx --test raw/附件二（测试集）.xlsx --output-dir outputs/q1_model_comparison`
Files / Hashes: See `evidence/evidence-ledger.yaml`.
status: OBSERVED
