# Ordinal Modeling

有序目标的类别之间有明确、可辩护的顺序，但相邻等级的距离通常不等于连续数值距离。只有题面、数据字典或明确的用户声明提供 `ordered_levels` 和 `ordering_source` 时，才可激活 ordinal workflow；整数编码本身不能证明顺序。

## Target Contract

- `nominal`：类别只有名称，没有可用顺序；使用 nominal classification 指标和模型。
- `ordinal`：类别有顺序，例如 `low < medium < high`；保存有序等级、来源、各等级计数和最少类别样本数。
- `continuous`：目标是有明确数值含义的连续量；不要为了得到等级而自动离散化。
- 顺序不清楚时记录 `UNVERIFIED` 并停止正式 ordinal 实验，不猜测顺序。

## Baselines And Metrics

先报告多数/最常见等级和按等级索引取中位数的 ordinal baseline。候选模型与 baseline 必须使用同一切分和协议。

除 Accuracy 外，至少报告等级索引上的 MAE、RMSE、Quadratic Weighted Kappa、Within-One-Level Accuracy 和 Large Ordinal Error Rate，并给出混淆矩阵。指标中的等级索引只表达已声明的顺序，不应被解释为连续物理单位。

## Candidate Models

低容量 cumulative ordinal logistic 是可解释候选：分别估计 `P(Y > level_k)`，然后检查累计概率单调性并转换成逐等级概率。仍应与 nominal multinomial baseline 同协议比较，不要求 ordinal 候选一定获得更高分。

连续回归后 clip/round 到等级只能作为明确标记的 `ordinal_approximation` baseline，不能冒充正式 ordinal likelihood。复杂模型只有在样本量、可验证性和解释需求支持时才进入候选。

## Validation And Probability Handling

- 每个等级都必须有训练和验证覆盖；`n_splits` 不得大于最小类别计数，稀疏极端等级不足时降低折数或停止验证。
- 目标存在患者、设备、用户、地点或时间结构时，不能静默退回普通 stratified CV；应改用 group-aware 或 temporal splitter。
- 所有预处理和特征选择必须在 CV pipeline 内拟合。概率行必须非负且和为 1；累计概率必须在阈值方向单调，不满足时 fail closed 或记录显式单调投影。
- prediction cutoff、Temporal Availability Contract 和 test-label 隔离规则优先于 ordinal 建模；纵向特征仍须先通过 temporal gate，再过滤后聚合。

## Reporting

实验记录最少保存 `ordered_levels`、`ordering_source`、`primary_metric`、`n_splits`、`n_repeats`、每 fold 类别覆盖和 probability/approximation 状态。跨模型比较必须说明相同数据范围、切分、指标和随机协议；不要只挑选对 ordinal 有利的指标或样本。
