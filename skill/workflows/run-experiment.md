# Run Experiment

## Purpose

用一致、可追踪协议运行和比较 Baseline、主模型与改进模型。

## Preconditions

模型、数据切分、指标和运行环境已定义；真实运行已获授权。

## Required Reads

- [`../rules/experiment.md`](../rules/experiment.md)
- [`../rules/evidence.md`](../rules/evidence.md)
- [`../references/imbalanced-classification.md`](../references/imbalanced-classification.md)
- [`../references/ordinal-modeling.md`](../references/ordinal-modeling.md)（运行 ordinal 候选或等级指标时）
- [`../references/group-validation.md`](../references/group-validation.md)（存在重复实体或 group-aware validation 时）
- [`../references/mechanism-closure.md`](../references/mechanism-closure.md)（运行机制、物理或动态模拟时）
- [`../references/spectral-conventions.md`](../references/spectral-conventions.md)（运行实际使用采样或频域量时）

## Inputs

模型实现、数据版本、特征、参数范围、随机种子和评估协议。

## Task Anchor

限定本轮实验问题、模型数、预算、主要指标和停止条件。

## Steps

1. 确认 `workspace-manifest.yaml` 中的 `ACTIVE_RUN_ID` 和唯一 `allowed_write_root`；没有 run-scoped workspace 时不得生成实验文件。
2. 从 [`../templates/experiment-record.yaml`](../templates/experiment-record.yaml) 创建结构化记录，先写 `planned_protocol` 和 `status: PLANNED`。机制实验同时从 [`../templates/mechanism-closure.yaml`](../templates/mechanism-closure.yaml) 创建 Closure Contract，并在正式运行前保存 `closure_status`、`allowed_claim_level`、`identifiability_status` 和 `numerical_termination_verified`。
   频域实验同时保存 Spectral Convention Contract；调用实际 FFT 库前完成采样恒等式、频率轴、归一化、复功率和变换 axis 记录。
3. 对涉及时间可得性、未来预测或纵向聚合的任务，先建立并通过 Temporal Availability Contract；必须在聚合前调用 temporal availability gate，确认 `feature_cutoff <= target_horizon`，并记录被排除的未来行。契约不是 `PASS` 时禁止生成 longitudinal features 或相应 OBSERVED metrics。重复实体必须明确 prediction setting；面向新实体时，先检查 group/类别可行性，再选择 splitter 并验证每 fold `overlap_count = 0`。任何 group leakage 都使 validation result `INVALIDATED`。二分类不平衡时先运行多数类基线，再按同一 split/metric 比较无权重与 `class_weight="balanced"` 等候选。ordinal 任务先验证等级顺序和最少类别样本数，再按同一 repeated CV 协议运行中位等级 baseline、nominal baseline 与 ordinal candidate，报告 MAE、RMSE、QWK、Accuracy、Within-One-Level Accuracy 和 fold 波动。预处理、特征选择、PCA、聚类、subgroup boundary、插补和重采样必须在训练 fold 内拟合，阈值只能用 validation 选择，不能读取 test labels。然后运行 Baseline，再运行主模型；每次改进尽量只改变一个可解释因素。全部产物写入 active run 的 `work/`、`outputs/` 或 `experiment-records/`，并在 Evidence Ledger 中登记稳定 `artifact_id`、路径和 SHA256。
   Stateful scheduling 先读 [`stateful-scheduling.md`](../references/stateful-scheduling.md)，把 Contract 写入 planned/executed protocol。正式 search 必须调用同一组 legal actions、transition 与 hard-invariant checks 来产生 candidate，或调用经验证的 feasible decoder。surrogate 只作为搜索优先级；incumbent 只比较真实 realized/decoded feasible objective，且候选记录 feasibility、components、runtime、termination 和 provenance。
   Structured improvement 另读 [`structured-improvement.md`](../references/structured-improvement.md)，把 move families、budget、acceptance 和 incumbent rule 写入 protocol。每个 candidate 必须经真实 realization/decoder 和 hard feasibility gate；surrogate 不能更新 incumbent；working solution 与 best feasible incumbent 分开记录。达到停止规则后保留 `evaluated_moves / feasible_moves / accepted_moves / incumbent_updates / termination_reason`，无改善时允许 `NO_IMPROVING_MOVE_FOUND`。
4. 运行前将 group 契约、实际 split IDs 和逐 fold fit provenance 通过 `apply_group_gate()` 写入 `group_structure`/`group_scope`；新实体泛化的实体交集非空必须 `INVALIDATED`。记录 `groups_used`、`group_key`、`split_strategy`、实际 `n_splits`、每 fold train/validation group IDs 与 counts、`overlap_count`。同实体新记录与同实体未来按各自 scope 检查，不要求错误的实体互斥；ENTITY_TIME 则必须独立通过 group 与 temporal gate。
5. 关联估计先读取 [`observational-association.md`](../references/observational-association.md)，在 protocol 中标 `association_analysis: true`，保存合同、实际 adjustment 和分析实体 IDs，经 `association_analysis.apply_association_gate()` 校验后运行粗/调整后模型。两个模型使用相同完整病例，记录暴露时序未知、稀有措施与共现限制。实体聚类区间只处理估计依赖；没有预测分数时明确不声称完成 grouped predictive validation。选择 propensity 方法时，先核验输入无 outcome/未来/处理后变量，并保存 overlap、weight、ESS、balance 诊断。
6. 运行后把真实 split、模型、敏感性、鲁棒性和指标写入 `executed_protocol`；用 [`../scripts/runtime_provenance.py`](../scripts/runtime_provenance.py) 自动计算 protocol diff。仅用于诊断的 row-random 结果不进入正式模型选择；最终全训练实体 curve fit 与 grouped CV 分开记录。
7. 若协议变化，填写原因、可比性和 `protocol_change_disclosure`；通过 validation gate 后才能在用户回答中接受 OBSERVED 数字。
8. 保存日志、预测/决策输出、指标、图表路径、失败信息和 run-bound evidence IDs。Stateful scheduling 另保存每个 incumbent 的 representation、feasibility mode、真实 objective、decision trace 或 decoder provenance；structured improvement 保存简洁 search trace 和 incumbent before/after。独立 final audit 仍必须从正式 result 重新检查硬约束。机制实验若依赖参数化输入或显式场景，结果文件和报告必须保留对应参数/假设；若 closure 未闭合，不得把运行数字写成唯一题目答案。
9. 报告绝对指标、相对变化、多种子/重采样波动与失败案例，并根据 Done When 决定 Keep/Reject。

特征集比较按需读取 [`feature-set-design.md`](../references/feature-set-design.md)，运行前将 `feature_set_comparison: true`、合同与 `feature_set` 扩展写入记录，先过 `feature_sets.audit_feature_comparison()`。复用实际 sample/fold IDs，逐 fold 保存 pipeline fit IDs；运行后过 feature gate，保存全部候选（含负结果）的配对指标。

## Checks

是否存在通过校验的 Experiment Record？机制实验是否存在通过校验的 Closure Contract？纵向特征是否在 temporal filtering 之后才聚合？是否记录 post-horizon 排除数量？Evidence Ledger 是否登记全部生成 artifact？配置能否复现？全部路径是否属于 ACTIVE_RUN_ID？如果计划与执行协议不同，
是否自动识别并显式披露变化原因？敏感性扰动是否标记为
`SIMULATED_PERTURBATION`？最好结果是否只是单次偶然？

## Outputs

`experiment-record.yaml`、结果表、失败日志、run-bound evidence、Keep/Reject 结论和下一实验假设。

## Stop Conditions

数据泄漏、指标实现错误、不可行解或运行与论文数字冲突时立即停止并修复。

## Handoff

交付可复现命令、数据/代码版本、最佳真实结果、Evidence Ledger 和未解决异常。

## Common Failure Modes

跑出好结果却忘记参数；只报最好种子；失败结果消失；测试集参与调参。
