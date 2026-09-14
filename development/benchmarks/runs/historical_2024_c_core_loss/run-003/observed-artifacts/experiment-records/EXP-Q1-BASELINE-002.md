# Experiment Record

Experiment ID: EXP-Q1-BASELINE-002
Problem: historical_2024_c_core_loss
Question: Q1
Model: StandardScaler + multinomial logistic regression (LBFGS)
Dataset / Version: 附件一（训练集）.xlsx; 附件二（测试集）.xlsx; run-003 immutable inputs
Feature Set: 26 features from 1024-point B(t): normalized distribution, first difference, second difference, slope and plateau summaries
Parameters: max_iter=1000; test_size=0.20
Random Seed: 42
Split / Validation: stratified random holdout, 9920 train / 2480 validation rows
Metrics: Accuracy=1.0000; Balanced Accuracy=1.0000; Macro Precision=1.0000; Macro Recall=1.0000; Macro F1=1.0000
Result (actual run / NOT RUN): ACTUAL RUN. Validation confusion matrix is diagonal: 811 / 990 / 679 correct for labels 1 / 2 / 3.
Attachment 2 prediction counts: 正弦波 20; 三角波 44; 梯形波 16.
Conclusion: The minimal baseline runs end-to-end and separates the three waveform labels on this random holdout. The perfect score is preliminary and may be optimistic if similar cycles cross the split; attachment 2 accuracy is NOT OBSERVED because labels are unavailable.
Keep / Reject: Keep as Q1 comparison baseline.
Environment / Command: `python work/q1_baseline.py --training raw/附件一（训练集）.xlsx --test raw/附件二（测试集）.xlsx --output-dir outputs/q1_baseline`
Files / Hashes: See `evidence/evidence-ledger.yaml`.
status: OBSERVED
Failure Notes: One earlier run was recorded separately as EXP-Q1-BASELINE-001 FAILED due to a deprecated scikit-learn argument.
