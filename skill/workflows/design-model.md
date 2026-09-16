# Design Model

## Purpose

基于问题结构设计 Baseline、候选模型族、主模型和失败回退路径。

## Preconditions

输入、输出、约束、数据可得性和验证协议已明确。

## Required Reads

- [`../rules/modeling.md`](../rules/modeling.md)
- [`../references/model-selection.md`](../references/model-selection.md)
- [`../references/models/index.md`](../references/models/index.md)
- [`../references/gotchas.md`](../references/gotchas.md)
- [`../references/imbalanced-classification.md`](../references/imbalanced-classification.md)
- [`../references/ordinal-modeling.md`](../references/ordinal-modeling.md)（目标有明确等级时）
- [`../references/group-validation.md`](../references/group-validation.md)（存在重复实体或纵向预测时）
- 只有在模型族确定后，读取对应模型族文件。

## Inputs

拆题结果、数据审计、资源限制、论文解释需求和验证条件。

## Task Anchor

限定当前子问题、最多比较的候选数、运行预算和完成标准。

## Steps

1. 先写 Baseline，再提出最多三个有实质差异的候选模型族。
2. 为每个候选记录目标、适用理由、假设、数据、数学形式、优势、缺点、最大风险、指标、实现/解释成本。
3. 检查模型是否能在现有数据与时间内验证；不能验证的只作为探索方案。
4. 如果任务涉及时间可得性、未来预测或纵向聚合，先建立并通过 Temporal Availability Contract；在 cutoff 过滤前不得设计或生成 longitudinal aggregate，边界不确定时只能停在 `UNVERIFIED`。重复实体依赖另由 group gate 检查；仅以已知 time 为坐标的描述曲线要明确其不声称日历未来预测。
5. 存在重复实体时先按 A/B/C/D 明确 prediction setting 与 ROW/ENTITY/TIME/ENTITY_TIME；新实体泛化必须将 group separation 置于完美 stratification 之上。在实例化 splitter 前检查独立 group 数、group size 和每个等级出现在哪些 groups；再检查实际 folds 的类别覆盖。训练 fold 缺等级应拒绝或改用合法协议，不能通过拆 group 修复。无时间外推的静态重复数据只激活 group gate。模型排名只能来自相同合法验证协议，row-random 与 grouped 的分数不得跨协议选优。
6. 二分类样本明显不平衡时，先纳入多数类基线；比较正则化 Logistic 与少量容量受控候选，并在同一协议下比较无权重和 `class_weight="balanced"`（若模型支持）。Accuracy 不能单独决定主模型，候选必须同时检查 PR-AUC、Balanced Accuracy、少数类 Recall、Precision、F1 和 Specificity。
7. 目标是 ordinal 时，先定义中位等级/最常见等级 baseline，再比较 nominal multinomial 与低容量 cumulative ordinal 候选；连续回归后取整只能标为 approximation，不作为正式 ordinal 模型。折数不得超过最少类别计数。
8. 对措施关系题先读取 [`observational-association.md`](../references/observational-association.md)，明确 estimand 和 claim_level；用同一样本的 `outcome ~ exposure` 与加少量处理前 confounders 的模型区分 crude / adjusted association。纵向结果选简单 mixed model、GEE、entity-clustered regression 或合法实体摘要；按题意加入少量 time × exposure，未知暴露时序只能解释 trajectory association。稀有或共现措施不做巨大组合搜索，propensity 不是默认要求。
9. 选择主模型、保底模型和改进假设；改进必须对应可观测缺陷。预先指定的关联估计不冒充预测选模；若比较新实体预测能力，仍使用合法 grouped validation。
10. 若声称创新，激活 `innovation-patterns.md` 与 Gotchas 的 Fake innovation 检查。

扩展信息场景按需读取 [`feature-set-design.md`](../references/feature-set-design.md)：保留合法 baseline，预先设计少量 B → B+G 与必要 Full−G 对照；固定样本、folds、模型与超参数/预处理政策。删除 baseline 显式记录原因，但该比较不能解释为纯增量价值。

## Checks

是否关键词套模型？复杂度是否带来可测收益？候选是否使用同一问题与验证协议？

## Outputs

模型比较矩阵、选择理由、Baseline、改进假设、停止条件和回退路线。

## Stop Conditions

无法定义评价/可行性检查或关键参数无来源时，不确认主模型。

## Handoff

向实验人员交付变量、公式、参数范围、数据切分、指标和预期产物。

## Common Failure Modes

现成算法当创新；列很多相似模型；忽略外推、可行性或参数可识别性。
