# Model Families Index

模型族是按需路由，不预先加载算法级百科。先读本索引，再按问题结构读取一个族文件。

| 问题/交付物 | Model Family | 内容 |
|---|---|---|
| 连续预测、时间序列 | [`prediction.md`](prediction.md) | Naive、线性、统计、树模型、Boosting、组合和误差修正 |
| 综合评价、排序、决策 | [`evaluation.md`](evaluation.md) | 等权、AHP、熵权、TOPSIS、稳健排序 |
| 资源分配、调度、路径、约束优化 | [`optimization.md`](optimization.md) | 规则、LP、MILP、NLP、GA、SA、多目标；动态状态可行性见 `stateful-scheduling.md` |
| 分类、聚类、降维 | [`classification-clustering.md`](classification-clustering.md) | 多数类、逻辑、树/集成、聚类、PCA |
| 动态机理、参数识别 | [`mechanism.md`](mechanism.md) | 回归、ODE、Markov、状态空间和残差混合 |
| 随机情景、Monte Carlo、网络 | [`simulation-network.md`](simulation-network.md) | Monte Carlo、仿真、图论、路径和鲁棒场景 |

每族都回答候选、适用/不适用、Baseline、数据、验证和常见误用；需要具体算法参数时再从外部资料或代码核验，不在 V2 预建单算法文件。
