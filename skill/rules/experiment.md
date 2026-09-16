# Experiment Rules

1. 任何 `run_experiment` 或 `validate_model` 产生 OBSERVED 数字前，必须创建或更新 [`../templates/experiment-record.yaml`](../templates/experiment-record.yaml)，并通过 `scripts/runtime_provenance.py validate-experiment`；Markdown 摘要不能替代该 artifact。
2. Baseline 与候选模型必须使用一致的任务定义、数据范围、切分和指标。
3. 预处理只在训练部分拟合；时间、空间、实体或组结构必须反映在切分中，防止泄漏。
4. 随机算法固定并报告种子；重要结论使用多种子、重采样或区间检查稳定性。
5. 测试集不用于选模型或调参；无法保留独立测试集时明确验证局限。
6. 失败实验也要记录原因，禁止只保留最好一次运行。
   特征组无明确增益也是有效结果；按需遵守 [`feature-set-design.md`](../references/feature-set-design.md)，在相同样本、folds、模型和政策下比较，保留合法 baseline、明确删除原因和逐 fold paired deltas。不可将样本组成或模型变化解释为信息增益。
7. 指标必须与误差代价和题目目标一致；报告边界情况与不可定义值。
8. `planned_protocol` 与 `executed_protocol` 使用稳定的结构化类型、参数和分组定义；`protocol_changed` 由 normalized protocol 自动比较生成，不由模型自行判断。
9. `protocol_changed: true` 时必须填写 `change_reason` 和 `comparable_to_original_plan`。状态为 `OBSERVED` 时还必须写入 `protocol_change_disclosure`，向用户说明原计划、实际执行、变化原因和新旧结果是否可直接比较。
10. 所有代码、模型、预测、指标、验证结果和 Experiment Record 必须写入 `ACTIVE_RUN_ID` 的 `allowed_write_root`；不得把共享桌面或旧 run 输出目录当 active workspace。
11. `SIMULATED_PERTURBATION`、重采样和诊断分析不等同于新增实测或重复实验。
12. 每个生成代码、输出、指标、图表和中间文件都要在当前 run 的 Evidence Ledger 或 Active Evidence Set 中登记稳定 `artifact_id`，并记录路径和 SHA256。
13. 对 longitudinal prediction，必须在 feature engineering 前通过 Temporal Availability Contract；`feature_cutoff` 不得晚于 `target_horizon`，且任何 post-horizon observation 进入聚合都会使实验 `INVALIDATED`。
14. 不平衡二分类的缩放、插补、特征选择、PCA 和重采样必须在训练 fold 的 pipeline 内拟合；test labels 不得参与模型、超参数或阈值选择。没有更强组/时间结构时优先 repeated stratified validation，并报告 fold 分布而非只报单一均值。
15. 重复实体任务必须先确定 `validation_unit` 和 prediction setting；面向新实体时所有同一 entity 的记录进入同一 fold，train/validation entity overlap 必须为 0。Group leakage 会使 validation result `INVALIDATED`；PCA、缩放、聚类和 subgroup boundary 也只能在 training groups 内拟合。
16. 新实体、同实体新记录、同实体未来和新实体未来的 scope 不可互换；GROUP 与 TIME 独立校验。通过 `apply_group_gate()` 保存 Group Structure Contract 和真实 fold IDs，再通过 experiment validator；记录必须能重算实体交集。未知 scope 不得默认 ROW；类别分层不能破坏 group separation，fold feasibility 必须在模型运行前检查。
17. `FIT_RESIDUAL` 只描述训练拟合；`VALIDATION_ERROR` 才描述相应 holdout 泛化。正式选模使用同一合法 group-aware 协议，最终可用全部训练 entities 重拟合曲线；row-random 泄漏对照不能参与选模。相关重复观测的 bootstrap 优先按 entity 抽样，不把行数当独立样本数。
18. 观察性措施分析先描述实体级暴露支持、初始特征、结局和 co-occurrence，再在同一样本比较 crude / adjusted association。记录 Association Analysis Contract 与实际调整项；通过 `association_analysis.apply_association_gate()` 接入 Experiment Record，处理后调整、未来/结局泄漏和不支持的因果等级不能发布为有效结果。
19. 纵向关联估计必须处理实体依赖，区间不得假定每行独立；若另外声称预测泛化仍需合法 Group / Temporal validation。稀有措施标 `ESTIMATE_UNSTABLE`；propensity 仅按条件选用，重叠、极端权重、ESS 和 balance 检查不能省略，也不等于因果识别。
