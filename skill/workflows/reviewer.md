# Reviewer

## Purpose

以数学建模竞赛网评专家视角寻找可证实的问题，不默认替作者辩护。

## Preconditions

提供论文、题面、关键代码/结果或明确说明缺失材料。

## Required Reads

- [`../rules/modeling.md`](../rules/modeling.md)
- [`../rules/evidence.md`](../rules/evidence.md)
- [`../references/gotchas.md`](../references/gotchas.md)
- [`../references/imbalanced-classification.md`](../references/imbalanced-classification.md)
- [`../references/ordinal-modeling.md`](../references/ordinal-modeling.md)（审查等级目标或 ordinal 结果时）
- [`../references/group-validation.md`](../references/group-validation.md)（审查重复实体或纵向验证时）

## Inputs

题面、论文、结果表、图、代码、数据说明、来源和 Competition State。

## Task Anchor

明确审查范围、是否可运行代码、优先级和 Done When。

## Steps

1. P0：未回答题目、数学逻辑错误、错误数据/泄漏、代码论文冲突、单位错误、不可行模型。
2. P1：无 Baseline、验证不足、选择理由弱、假设不合理、结论缺数字、创新不成立。
3. P2：图表解释、符号一致、章节逻辑、公式说明。
4. P3：语言、排版、图表美化和术语统一。
   Stateful scheduling 另查三类错误：动态状态决定可行性却先优化理想排列再映射，报告 `STATE_FEASIBILITY_DECOUPLED`；硬约束非法动作只加大 penalty，报告 `HARD_CONSTRAINT_AS_PENALTY`；用抽象排列 surrogate 证明最佳调度，报告 `SURROGATE_OBJECTIVE_AS_FINAL`。合法 `SEQUENCE_WITH_FEASIBLE_DECODER` 不应被仅因使用排列而否定。
5. 对时间数据、分类不平衡指标和创新声明逐条激活 Gotchas；对纵向预测沿 `target_time -> feature availability -> aggregation window` 复核 Temporal Availability Contract。任何 `feature time > allowed cutoff` 或先聚合后过滤都报告 `P0 FUTURE_INFORMATION_LEAKAGE`，给出证据位置、影响、最小修复和复核标准。
6. 对 ordinal 结果核验等级顺序来源、距离感知指标、稀疏等级的 fold 覆盖和概率合法性；未声明的回归取整或不同协议比较属于验证缺陷。
7. 先核对预测场景：声称新实体泛化却对重复观测做 random row split，要求真实 fold entity IDs；有重叠则报告 `P0 GROUP_LEAKAGE`、`INVALIDATED`，不能只 warning。未提供 ID 证据时报告 GROUP_LEAKAGE 风险并保持 UNVERIFIED。把全部 longitudinal rows 宣称为独立 n，报告 `PSEUDOREPLICATION / DEPENDENCE ISSUE`。同实体未来场景允许实体重叠，但时间 gate 仍须单独通过。检查 `FIT_RESIDUAL` 是否被冒充 `VALIDATION_ERROR`、PCA/缩放/聚类/分组边界的实际 fit rows 是否仅在 training fold、row bootstrap 是否错误宣称独立不确定性。不同 split 协议的模型分数不能直接排名。
8. 对不平衡二分类复核类别分布、多数类基线、分层/组/时间验证、fold 波动、PR-AUC 相对正类流行率、少数类 Recall 与阈值来源。若任务重视少数类而候选少数类 Recall 为 0，即使 Accuracy 很高也不能标为 `VALID FINAL MODEL`；若 test labels 参与阈值选择，或 SMOTE/特征选择/PCA/插补/缩放在 split/CV 前拟合，报告 `P0 DATA_LEAKAGE`。
9. 观察性关系题先读取 [`observational-association.md`](../references/observational-association.md)，复核 Association Analysis Contract：病情/需求/风险影响措施分配的混杂、处理前 confounder 证据、暴露时序、实体依赖、稀有措施及共现。把处理后变量作为普通 confounder 或把 outcome 放入 propensity model 属于分析失效。无可靠识别却写“导致”“使得”“有效降低”“增加风险”等因果表述，报告 `P1 UNSUPPORTED_CAUSAL_CLAIM` 并将该 Claim `INVALIDATED`；使用 `association_analysis.review_association_claim()` 辅助检查，同时逐条审查上下文。未知时序只能报告 association / trajectory association；randomization、matching、IPTW 或调整回归的名称本身不能替代设计证据。
10. 对照 ACTIVE_EVIDENCE_SET 和 Evidence Ledger 检查每个 Paper Claim 的 `run_id/experiment_id/artifact_id`。引用其他 run 且未标为 historical 时报告 `STALE_EVIDENCE_REFERENCE`；主动发现并阻止旧证据混用属于 Reviewer 正确行为，不是 model-behavior P0。

出现特征筛选或新增信息增益声明时按需读取 [`feature-set-design.md`](../references/feature-set-design.md)，用 `review_feature_claim()` 核查受控证据。静默删 baseline/换样本/换 folds 或模型报 UNCONTROLLED_FEATURE_SET_COMPARISON；全数据先筛选再 CV 报 FEATURE_SELECTION_LEAKAGE；无依据大组合选最高分报 FEATURE_SET_SEARCH_OVERFIT_RISK；来源、时点或构造不全报 FEATURE_PROVENANCE_INCOMPLETE。

## Checks

是否用作者意图替代证据？是否先列 P0/P1？无法核验处是否标 `[需要验证]`？

## Outputs

使用 [`../templates/reviewer-report.md`](../templates/reviewer-report.md) 输出 P0-P3、总体状态和修复顺序。

## Stop Conditions

缺少题面或论文主体时，只做材料完整性审查，不声称完成全面 Reviewer。

## Handoff

把必须修复、建议修复、复核方法和剩余风险写入 Competition State。

## Common Failure Modes

默认替作者找借口；先改措辞而忽略数学错误；无证据地判定文献或结果真实。
