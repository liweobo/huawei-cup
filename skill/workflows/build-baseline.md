# Build Baseline

## Purpose

建立可运行、可解释、可复核的最小比较基准。

## Preconditions

任务定义、数据切分和主要指标已固定。

## Required Reads

- [`../rules/modeling.md`](../rules/modeling.md)
- [`../rules/experiment.md`](../rules/experiment.md)

## Inputs

子问题、数据、指标和主模型候选。

## Task Anchor

明确 Baseline 用来比较什么，不在本轮扩展复杂调参。

## Steps

1. 选择最少假设且可复核的方法：预测可用 Naive/线性，优化可用规则/贪心，评价可用等权分数，聚类可用业务规则。
2. 按与主模型相同的切分和指标真实运行，记录配置和产物。
3. 检查结果是否足以发现数据/指标/代码错误。
4. 写明主模型预期改善的具体指标或约束表现。
5. 措施关系题先读取 [`observational-association.md`](../references/observational-association.md)，以描述性组间比较和 crude association 作为比较基准，再在同一完整病例上加入少量已验证的处理前变量。系数变化不能称作“效果改善”；重复观测按 entity 处理依赖，并保留暴露时序与 claim_level 边界。

## Checks

Baseline 是否过弱或使用不同数据？是否真实运行？是否能支撑失败回退？

## Outputs

基线定义、真实结果或 `NOT RUN`、误差分析和比较协议。

## Stop Conditions

Baseline 无法运行时，先修复数据/指标链而不是继续堆复杂模型。

## Handoff

把配置、结果和主模型必须超过的比较目标交给实验流程。

## Common Failure Modes

把占位规则称 Baseline；不同切分比较；只保留复杂模型最好结果。
