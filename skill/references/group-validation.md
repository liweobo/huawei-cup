# Longitudinal And Group-Aware Validation

重复观测的独立抽样单位通常是 entity，而不是 observation row。先回答模型最终泛化到什么，再选择 validation unit；实体内相关性、未来信息和类别不平衡是不同问题，分别检查。

## Validation Scope

| 最终预测场景 | prediction_setting | validation_unit | 必须满足 |
|---|---|---|---|
| A. 已知实体的新记录，无时间外推 | SAME_ENTITY_RECORD | ROW | 明确此条件预测场景；验证实体在训练中有历史，预处理只拟合训练记录 |
| B. 从未见过的新实体 | NEW_ENTITY | ENTITY | 完整实体留出；train 与 validation entity 交集为空 |
| C. 同一实体的未来记录 | SAME_ENTITY_FUTURE | TIME | 合法时间向前切分、feature cutoff；实体重叠可符合题意 |
| D. 新实体的未来记录 | NEW_ENTITY_FUTURE | ENTITY_TIME | 实体不重叠，且时间切分与信息可得性分别通过 |
| 真正独立静态样本 | INDEPENDENT_ROWS | ROW | 无重复实体依赖；允许普通 row CV |

未知场景保持 `UNVERIFIED`，不能自动默认 ROW，也不能仅因重复记录就一律使用 GroupKFold。`GROUP_LEAKAGE` 的实体不重叠规则适用于 B/D；不能用这条规则错误否定 A/C。没有时间预测或时间特征的静态重复测量，不凭空要求时间戳。

## Group Structure Contract

`audit-data` 自动查找重复 identifier 候选；候选使用字段命名结构（如 `*_id`、`*_key`、`*Id`）及重复计数，不依赖某个领域。字段名不能证明实体语义：确认附件数据字典；无标准命名时显式提供 `entity_key`。多个候选分别报告统计量，不自动选择其中一个。缺失 ID、空表、场景不明或身份未确认均保持 `UNVERIFIED`。

```yaml
entity_key: entity_id
prediction_setting: NEW_ENTITY
validation_unit: ENTITY       # ROW / ENTITY / TIME / ENTITY_TIME
unit_of_analysis: ENTITY
n_entities: 100
n_rows: 450
min_rows_per_entity: 2
median_rows_per_entity: 4
max_rows_per_entity: 9
repeated_entities: 100
status: PASS
```

以上数字仅为 schema 示例，真实字段来自审计。使用 `scripts/data_audit.py --group-context <JSON>` 传入 `entity_key`、`prediction_setting`，必要时加入聚合 provenance。即使未确认候选 key，仍报告各候选的实体数和每实体行数。

目标为新实体时，同一 entity 的全部记录必须完整进入同一 fold，`train_entity_ids ∩ validation_entity_ids = ∅`。Temporal leakage 指未来信息进入过去预测；Group leakage 指新实体评估中共享了实体。一个任务可独立触发二者，修好其中一个不代表另一个通过。

## Split Selection

- 新实体：使用 `GroupKFold`；分类且每个等级分布在足够多的 groups 时可使用 `StratifiedGroupKFold`。
- 在运行 sklearn 前检查 group 数、group size 和每个 target level 覆盖的 group IDs/计数；4 groups 请求 5 folds 必须拒绝，或明确降低 folds 并记录实际协议。
- binary / multiclass / ordinal 都优先保留实体独立性，再争取类别覆盖。`StratifiedGroupKFold` 只是近似分层，预检后还要检查实际 folds。分层不可行时可 `FALLBACK_GROUP_ONLY`，或降低 folds，绝不拆 entity。训练 fold 缺等级时拒绝该协议；验证 fold 缺等级时记录具体缺失，AUC 等不可定义指标不得静默忽略该 fold。
- `TIME`/`ENTITY_TIME` 使用符合日历时间或实体内时间定义的向前切分；需要时先留出新实体再约束时间窗口。`group_cv_splits()` 明确拒绝用普通 GroupKFold 生成这两种协议。自定义 split 交给 `validate_group_cv_splits()` 检查实体，再独立验证时间顺序与 Temporal Availability Contract。只有 group gate PASS 不能发布未来预测结论。
- 已合法聚合成一实体一行时，普通 KFold 的 row split 可等价于 entity split，元数据仍为 `unit_of_analysis=ENTITY`、`validation_unit=ENTITY`。声明 `aggregated_from_repeated=true` 并验证聚合 provenance：`within_entity_only=true`、时间 gate PASS（不涉及时间时说明 NOT_APPLICABLE 理由）、学习型预处理 NONE/TRAIN_FOLD。聚合来源未知不能凭表面唯一 ID 通过。

正式记录包含 `groups_used`、`group_key`、`split_strategy`、`n_splits`，以及每 fold 的 train/validation row IDs、entity IDs、group counts、`overlap_count`。B/D 的 overlap 必须为 0；发现重叠立即 `GROUP_LEAKAGE → INVALIDATED`，不能只 warning。

`audit_group_cv_splits()` 可保留失败对照的完整证据；`validate_group_cv_splits()` 则抛出错误。`runtime_provenance.apply_group_gate()` 把 Group Structure Contract 与 split report 写入 Experiment Record 的 `group_structure`/`group_scope` 并自动 invalidation；`validate-experiment` 会重算实体交集，拒绝伪填的零重叠、缺失契约和未验证的 OBSERVED。与 `apply_temporal_gate()` 组合时保留两个 gate 的独立状态和失败原因。

## Longitudinal Curves And Subgroups

纵向回归 `outcome=f(time)` 同样需要完整实体留出；不能把不同时间点当作独立训练样本和验证样本。拟合残差 `FIT_RESIDUAL = observed - fitted` 只描述拟合样本；`VALIDATION_ERROR = observed - held_out_prediction` 才用于对应预测场景的泛化评价。残差很小不能推出泛化很好。

题目要求全体样本曲线与残差时，正常流程是 `Model Selection: grouped CV`，随后 `Final Fit: all available training entities`。最终曲线和完整训练残差另存，不能回填为 CV 结果，也不能把 held-out/test 实体并入“全部训练”。

任何 PCA、缩放、聚类、trajectory clustering、分组边界都必须在每个 training fold 内拟合，再对 validation transform/predict/assign。未使用 target 不能证明无泄漏。使用完整 sklearn Pipeline 并逐 fold clone；不能先全量 PCA 再把变换后的矩阵传入 CV。

`validate_unsupervised_scope()` 核对真正传给 fit 的 `fit_row_ids` 是否包含于训练集合，且不与验证集合相交；仅声明 `fitted_inside_fold=true` 保持 UNVERIFIED。记录 fit 输入的行 ID，不能事后把预期 train IDs 当作实际 fit provenance。

亚组发现也在 training groups 中进行：从每个训练实体的合法 baseline 特征拟合 quantile 边界或 clustering；验证实体仅使用预测当时可得的 baseline 特征分配亚组，再应用训练出的 subgroup trajectory。baseline outcome 用于分组时，不把同一 baseline outcome 的回预测作为未来验证成绩。对全验证轨迹计算均值/斜率来分配未来预测亚组仍可能是时间泄漏。规则若由题面事先固定则记录来源，不必把固定常数伪装为学习步骤。

## Uncertainty And Reporting

重复观测相关时，bootstrap unit 优先为 entity：有放回抽 entity，每次保留抽中实体的全部记录及抽样次数。普通 row bootstrap 不能标为独立不确定性估计。有效独立单位更接近实体数，不能把多次观测宣称为同样数量的独立样本；确切有效样本量仍取决于相关结构，实体之间也须满足所用方法的独立假设。

Reviewer 面对重复观测加 random row split 且声称新实体泛化时，要求实际 entity IDs；已有重叠报告 `P0 GROUP_LEAKAGE / INVALIDATED`，缺乏 ID 证据则报告 `GROUP_LEAKAGE` 风险并保持 UNVERIFIED。把 observation 数量写成独立 n，报告 `PSEUDOREPLICATION / DEPENDENCE ISSUE`。`review_group_validation()` 支持上述结构化检查；论文审稿还需核对源代码与误差口径。

回归沿用 MAE、RMSE、适用时 R²；分类沿用既有 ROC-AUC、PR-AUC、Balanced Accuracy、Recall 等；ordinal 沿用 MAE、RMSE、QWK、Within-One-Level。不得因本能力另建 metric 系统。说明分数是 observation-weighted 还是 entity-weighted；不同记录数使两种估计对象不同，不能静默互换。

模型选择只比较同一 target、features、合法 split 和 metric 协议。A 的 row-random RMSE=5 与 B 的 grouped RMSE=8 不能直接排优劣。泄漏诊断可固定同一模型和特征比较两种切分；row-random 数字始终是 INVALIDATED 对照，不参与选模。差值只反映该模型和该切分下的观测差异，未保证每次 row 分数都更好，也不能由小差值认定无泄漏。
