# Optimization Model Family

## Candidates

规则/贪心、LP、MILP、NLP、GA、SA、ε-约束或其他多目标方法。先判断变量连续/离散、目标/约束线性与否，再决定精确或启发式路线。

## Fit

决策变量、目标、边界和约束能被明确写出；单位和资源守恒闭合；求解状态可解释。

如果动作合法性取决于机器、队列、buffer、位置、release、precedence 或其他随动作变化的状态，读取 [`stateful-scheduling.md`](../stateful-scheduling.md)，先建立 Stateful Scheduling Contract。此时不能只生成抽象 permutation / target sequence，再在求解结束后检查是否可执行。

如果已经得到合法 feasible incumbent、没有 exact OPTIMAL proof，并且改变少量离散决策可能改善真实 objective，读取 [`structured-improvement.md`](../structured-improvement.md) 并建立 Structured Improvement Contract。它负责在合法搜索空间中定义 meaningful move families、acceptance、budget 和 monotone incumbent，而不是新增 GA/SA/CP-SAT 等 solver。

## Baseline / Primary

规则、贪心或简单分配是 Baseline；LP/MILP/NLP 在规模和假设允许时优先于启发式；GA/SA 通常是 Improved/备选，必须多种子和可行性检查。

## Data / Validation

报告目标值、约束违约/可行率、整数性、最优 gap、运行时间、多初值/多种子、场景损失和实际可执行性。

## Common Misuse

看到“优化”就用遗传算法；把局部/启发式最好解称全局最优；Big-M/罚项无来源；四舍五入后破坏约束。

把动态状态可行性推迟到 post-hoc simulator；优化 target permutation 的 surrogate，却用该 surrogate 选择最终 incumbent；或者把硬约束非法动作当作大 penalty 后继续扩展。

有可行解却只重复随机生成完整解，没有 decision-semantic move 与 incumbent 对比；或者把 temporary working solution 的变差误写成 best incumbent 变差。
