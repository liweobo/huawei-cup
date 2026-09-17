# Model Selection

## Decision Frame

`问题结构 -> 数据可得性 -> 假设 -> 约束 -> Baseline -> 候选模型族 -> 验证 -> 复杂度/解释性`

| 问题结构 | 保底 Baseline | 可比较模型族 | 首要验证 |
|---|---|---|---|
| 连续/时序预测 | 均值、Naive、线性 | prediction | 时间/留出回测、MAE/RMSE |
| 分类 | 多数类、逻辑回归 | classification-clustering | 分层/组切分、F1/AUC |
| 无标签分组 | 业务规则 | classification-clustering | 内部指标、稳定性、解释 |
| 多指标排序 | 等权分数 | evaluation | 权重/标准化敏感度、排名稳定 |
| 线性资源分配 | 规则/贪心 | optimization | 可行性、目标、资源守恒 |
| 离散逻辑调度 | 规则/贪心 | optimization | 约束、gap、运行时间 |
| 动态资源/队列/缓冲调度 | 规则/贪心 | optimization + stateful-scheduling | legal actions、transition、hard invariants、真实 objective |
| 已有可行 incumbent 的组合优化 | 可行构造/贪心 | optimization + structured-improvement | move semantics、feasible realization、真实 objective、budget |
| 连续机理/动态 | 简化方程/差分 | mechanism | 参数识别、轨迹、守恒 |
| 随机风险/网络 | 确定性情景/直接距离 | simulation-network | 收敛、扰动、可达性 |

候选模型必须说明适用假设、数据需求、数学接口、最大风险、评价和解释成本。模型族只在问题类型已确认后加载；不要因为“预测/评价/优化”一个词直接选择算法。

存在重复实体时先读取 [Group-Aware Validation](group-validation.md)。同一个实体不能同时参与新实体模型的训练和验证；只有同一合法 scope、split、features 和 metric 的成绩才可用于模型排名。先通过 grouped validation 确定方法，再用全部训练实体拟合最终曲线；训练 residual 与 out-of-entity error 分开报告。
