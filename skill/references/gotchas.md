# Gotchas

本文件只沉淀在真实赛题测试中反复发生或具有高风险的错误。每条包含 `Failure` 与 `Activation`；没有 Activation 的经验不算已接入流程。

## Negation routing

**Failure**：用户明确说“不要建模/先别选模型”，路由仍因出现“建模/模型”进入 `design_model`。

**Activation**：Routing 在累加正向模型信号前检查否定范围；明确请求的分析、数据、Baseline、论文或验证意图优先。

## Time-series leakage

**Failure**：时间序列随机切分，或使用预测时不可获得的未来字段。

**Activation**：`audit-data`、`validate-model`、`reviewer` 遇到时间字段/时序目标时，必须检查时间因果、滚动切分和特征可得时点；随机 shuffle 或 8:2 随机切分不得直接作为时序验证协议。

## Temporal availability before longitudinal aggregation

**Failure**：为预测未来结局直接汇总实体的全部重复观测，之后才发现部分观测发生在目标时间之后。

**Activation**：只要预测/分类/回归使用时间、重复观测或纵向数据，先确定 `prediction_as_of_time`、`target_time` 和 `allowed_feature_horizon`，再过滤观测并核验无 post-horizon 行，最后才生成 last/max/mean/slope/change 等聚合特征。边界无法确定时为 `UNVERIFIED` 并阻止正式实验；未来行进入聚合是 `P0 FUTURE_INFORMATION_LEAKAGE`。

## Class imbalance metric trap

**Failure**：类别严重不平衡时只报告 Accuracy，或在全量数据上重采样/特征选择/调阈值后再验证。

**Activation**：分类任务在 `audit-data`、`design-model`、`run-experiment`、`validate-model` 和 `reviewer` 检查类别分布；明显不平衡时加载 [`imbalanced-classification.md`](imbalanced-classification.md)，比较多数类基线，报告少数类与概率指标，并把重采样/预处理放入 CV pipeline、把阈值选择限制在 validation。

## Group leakage and pseudoreplication

**Failure**：重复观测按行随机切分，使同一 entity 同时出现在训练和验证；或把所有 longitudinal rows 宣称为独立样本。

**Activation**：`audit-data`、`design-model`、`run-experiment`、`validate-model` 和 `reviewer` 发现重复实体时建立 Group Structure Contract。面向新实体泛化必须使用 group-aware splitter，检查每 fold `overlap_count = 0`；row split、row bootstrap 或 in-sample residual 不得冒充 entity-level validation evidence。若同时存在时间边界，独立执行 Temporal Availability Gate。

## Fake innovation

**Failure**：把使用 XGBoost、TOPSIS、LSTM 或遗传算法本身当作创新。

**Activation**：`design-model`、`write-paper` 和 `reviewer` 的创新声明必须回答修改内容、合理性和同协议实验改善。

## Outlier overreaction

**Failure**：把 IQR/统计提示直接变成自动删除规则。

**Activation**：`audit-data` 只输出提示；任何删除、截尾或插补都要有题意依据、实验记录和敏感性检查。

## Rule drift

**Failure**：沿用旧年份比赛规则或把未核验信息写成允许。

**Activation**：`final-check` 必须读取 `references/competition/2026-rules.md`，关键项为 `UNVERIFIED` 或 `OUTDATED` 时不得判 READY。

## Workflow promise exceeds script capability

**Failure**：Workflow 声称工具会自动发现风险，但脚本实际上只能输出候选或运行用户提供的场景。

**Activation**：凡 Workflow 使用“自动检测/自动识别/自动判断”等表述，必须核对对应脚本与测试；能力不足时改写为“检查、辅助识别、提示候选、需要进一步验证”。

## AAR maintenance

每次真实历年题测试后固定回答：是否发现新模式？新陷阱？缺失规则？过时规则？单次经验先进入本文件；重复稳定经验升级到 `rules/`；高风险普遍原则才进入 `SKILL.md`。
