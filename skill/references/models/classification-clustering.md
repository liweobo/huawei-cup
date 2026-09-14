# Classification and Clustering Model Family

## Candidates

分类：多数类、逻辑回归、树/随机森林/Boosting、校准和代价敏感模型；目标有明确等级时，补充 ordinal baseline、cumulative ordinal candidate 和距离感知指标。聚类：业务规则、K-means、层次、密度和共识方法。PCA 是预处理/探索工具。

## Fit

分类有可信标签和类别代价；ordinal 分类还必须有可追溯的等级顺序和稀疏类别可行性检查。聚类没有可靠标签且距离/相似度有业务意义。尺度、缺失和组结构必须明确。

## Baseline / Primary

多数类/逻辑回归和业务规则是 Baseline；有序目标先加入中位等级 baseline，再与 nominal multinomial 和可解释 cumulative ordinal 候选同协议比较。树集成或稳定可解释聚类才可作 Primary。PCA 不因解释方差高就自动成为主模型。

## Data / Validation

分类检查类别分布并报告 Precision/Recall/F1/AUC/混淆矩阵；ordinal 分类补充 MAE、RMSE、Quadratic Weighted Kappa 和等级误差分布；聚类报告三种内部指标、种子/尺度稳定性和业务画像。

## Common Misuse

不平衡只报 Accuracy；随机切分组数据；把簇标签当真实类别；用二维图决定簇数；全量标准化导致泄漏。
