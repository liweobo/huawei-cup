# Competition State

Status: IN PROGRESS
Last Updated: 2026-09-03

ACTIVE_RUN_ID: run-003
Workspace Manifest: `workspace-manifest.yaml`
Allowed Write Root: `C:\Users\aaa\Desktop\test\huawei-cup-2026\benchmarks\runtime\historical_2024_c_core_loss\run-003`
Prior Run Artifacts Visible: false
ACTIVE_EVIDENCE_SET: `evidence/active-evidence-set.yaml`
Active Files Projection: task-anchor.md, competition-state.md, work/data-audit-summary.json, work/attachment1-data-inspection.md, work/q4-output-alignment-check.md, paper/numeric-evidence-audit.md

Selected Problem: 2024 研究生数学建模竞赛 C 题
Domain Context: 磁性元件磁芯损耗；波形识别、经验方程修正、因素分析、数据驱动预测、多目标优化
Current Phase: Q1 候选模型比较已运行

Q1: BASELINE + RF + RBF-SVM OBSERVED (EXP-Q1-MODEL-COMP-003); all tied on current holdout; leakage-aware validation pending
Q2: FORMULATION READY; fit/error comparison NOT RUN
Q3: ANALYSIS PLAN READY; interaction model NOT RUN
Q4: MODEL DESIGN PENDING Q1 FEATURES; train/test prediction NOT RUN
Q5: OBJECTIVE FORMULATION READY; optimization NOT RUN

Data Audit: COMPLETED (read-only, run-003)
Baseline: Q1 observed; 26 B(t)-shape features + StandardScaler + LogisticRegression; validation Macro F1=1.0000
Primary Model: NOT SELECTED; RF and RBF-SVM show no observed gain over baseline
Validation: NOT RUN
Sensitivity: NOT RUN
Robustness: NOT RUN

Paper Status: outline only
Code Status: Q1 baseline and candidate comparison code run and recorded; Q2-Q5 code NOT RUN
References Status:题面内置参考文献已识别，外部核验未做

P0 Risks: 题面公式为嵌入图片，当前环境未完成渲染/OCR
P1 Risks: 采样序列的周期边界、磁通密度峰峰值定义、温度/材料分层验证方案需在正式实验前固定

Current Task: 论文数字证据准入审计
Next Highest-Value Action: 对三种模型执行按材料/工况分组的防泄漏验证，并与更简单特征子集比较；不直接把随机留出满分当作最终泛化结论
