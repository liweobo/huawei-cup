# Validate Model

## Purpose

判断模型的泛化、约束可行性、参数敏感性和结论鲁棒性。

## Preconditions

已有真实实验记录；没有运行结果时只能制定验证计划。

## Required Reads

- [`../rules/experiment.md`](../rules/experiment.md)
- [`../references/evaluation-metrics.md`](../references/evaluation-metrics.md)
- [`../references/gotchas.md`](../references/gotchas.md)
- [`../references/imbalanced-classification.md`](../references/imbalanced-classification.md)
- [`../references/ordinal-modeling.md`](../references/ordinal-modeling.md)（验证有序目标时）
- [`../references/group-validation.md`](../references/group-validation.md)（验证重复实体或纵向模型时）
- [`../references/mechanism-closure.md`](../references/mechanism-closure.md)（验证机制、物理或动态模拟时）

## Inputs

模型、数据切分、预测/决策输出、参数、指标和 Baseline。

## Task Anchor

明确要验证的结论、可接受误差/违约、扰动范围和不做的额外调参。

## Steps

1. 读取当前实验的 [`../templates/experiment-record.yaml`](../templates/experiment-record.yaml) 实例和 `workspace-manifest.yaml`。若验证会新运行代码、新增 split/敏感性/鲁棒性、修改模型或指标，先把记录改为 `RUNNING`。
2. 检查切分是否尊重时间、空间、实体和信息可得时点。先明确 validation scope；新实体泛化才强制每 fold entity overlap=0，同实体未来预测允许已有实体历史但必须满足时间约束。纵向时间特征复核 Temporal Availability Contract、`feature_cutoff` 与 `target_horizon`，确认聚合输入先经过 cutoff 过滤。Group Structure Contract 和实际 split IDs 通过 `runtime_provenance.apply_group_gate()` 接入记录；发现 post-horizon 行进入聚合或新实体评估出现重叠，独立报告 `FUTURE_INFORMATION_LEAKAGE` / `GROUP_LEAKAGE` 并 `INVALIDATED`。缺失或未验证契约不得发布 OBSERVED；只通过 group gate 不能代替时间验证。机制模型同时复核 Closure Contract：缺失 essential initial state 应降级为 `PARAMETRIC` 或 `UNVERIFIED`；若在声明模型范围内所有条件已闭合，则可为 `CLOSED_FOR_UNIQUE_NUMERICAL`，但仍单独报告模型形式不确定性与物理真实性限制。
3. 按任务读取指标原则；分类先检查类别分布，激活 Class imbalance metric trap。明显不平衡时必须比较多数类基线，并报告 ROC-AUC、PR-AUC（附正类流行率）、Macro F1、Balanced Accuracy、少数类 Recall、Precision、F1 和 Specificity；概率任务补充 Brier score 与校准说明。Accuracy 不能作为唯一或主要选模依据。若使用决策阈值，只能在 validation/inner validation 选择并在 test 前冻结。
4. ordinal 任务复核 `ordered_levels` 与 `ordering_source`，确认每 fold 覆盖全部等级、概率归一化且累计阈值概率单调；回归取整必须显式标记 approximation。与 Baseline 比较泛化指标、失败案例和实际意义；优化额外检查全部约束。
   stateful scheduling 额外核验 candidate representation、feasibility mode、legal-action gate、transition invariant、terminal completeness 和 incumbent selection。`SEQUENCE_ONLY` 无 decoder、post-hoc-only 正式候选、surrogate 冒充真实 objective 或 infeasible candidate 击败 feasible incumbent 时，验证状态 `INVALIDATED`。
   structured improvement 额外核验 move family provenance、hard feasibility gate、真实 objective、working/incumbent 分离、MAX/MIN 方向、budget、stopping rule、trace 与 incumbent 单调性。出现 `UNSTRUCTURED_OPTIMIZATION_SEARCH`、`INFEASIBLE_NEIGHBOR_AS_VALID`、`SURROGATE_IMPROVEMENT_CLAIM`、`IMPROVEMENT_EVIDENCE_MISSING` 或 `SEARCH_BUDGET_UNSPECIFIED` 时，不能把 improvement 结果作为正式结论。
5. 纵向曲线分别保存全训练拟合的 `FIT_RESIDUAL` 与完整实体留出的 `VALIDATION_ERROR`，最终全量重拟合不能替代 grouped model selection。PCA、缩放、聚类和 subgroup boundary 记录实际 fit 输入 IDs，验证其仅来自当前 training fold；验证实体仅按训练规则分配亚组。bootstrap 存在重复实体时优先以 entity 为单位，保留抽中实体全部观测；不能把 correlated rows 视为独立 n 或把 fold 标准差写成置信区间。
6. 关联分析先读取 [`observational-association.md`](../references/observational-association.md)，复核 assignment、处理前证据、暴露时间和 estimand，确认 crude / adjusted 在同一样本上比较；变化只解释为关联或可能混杂。纵向估计按 entity 处理依赖，稀有措施标 `ESTIMATE_UNSTABLE`；若使用 propensity 检查 overlap、极端权重、每侧 ESS 和前后 balance。不存在可靠识别时，不得用模型收敛、显著系数或 balance 通过来升级因果 claim。
7. 灵敏度：用 `scripts/sensitivity.py` 对关键参数做 `θ × (1 ± δ)` 或有依据的非对称扰动；baseline 为 0 时只解释绝对变化，除非显式提供有领域含义的 normalization scale。
8. 鲁棒性：用 `scripts/robustness.py` 运行用户定义的命名情景，比较参数、噪声、样本、种子、极端情景或初值变化是否改变结论；该脚本是 scenario runner，不自动生成这些扰动。
9. 把实际验证完整写入 `executed_protocol`，由 [`../scripts/runtime_provenance.py`](../scripts/runtime_provenance.py) 自动计算 `protocol_changed`。变化时填写 reason、可比性和用户披露；校验通过后才能把记录标为 `OBSERVED`。
10. 所有 validation evidence 绑定当前 `run_id` 和 `experiment_id`，并明确适用边界、断裂证据链和待补数据。机制验证还要分别记录 `MODEL_CLOSURE`、`NUMERICAL_CONVERGENCE` 和 `MODEL_VALIDITY`；其中一个通过不能替代另外两个。

评估信息增益时按需读取 [`feature-set-design.md`](../references/feature-set-design.md)，核对 same-sample、baseline retention、固定 folds/model/policies 和 fold-safe selection。按指标方向报告 paired mean/median delta、标准差与 sign consistency；小而不稳定的差异记 NO_CLEAR_INCREMENTAL_VALUE。维度和缺失成本上升但无明确收益时允许选择简单集合。

## Checks

验证产生的新数字是否更新了 Experiment Record？路径是否属于 active run？是否只看训练拟合？是否存在 data leakage？协议变化是否披露？灵敏度/鲁棒性扰动是否有题意？

## Outputs

更新后的 `experiment-record.yaml`、验证表、灵敏度表、鲁棒性情景、run-bound evidence、适用边界和失败案例。

## Stop Conditions

发现泄漏、不可行解或评价函数错误时，验证失败并回到数据/实验流程。

## Handoff

向论文流程交付可引用的真实指标、图表、局限和验证结论。

## Common Failure Modes

时间随机切分；不平衡分类只报 Accuracy；扰动无依据；把训练结果写成泛化能力。
