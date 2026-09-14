# Optimization Model Family

## Candidates

规则/贪心、LP、MILP、NLP、GA、SA、ε-约束或其他多目标方法。先判断变量连续/离散、目标/约束线性与否，再决定精确或启发式路线。

## Fit

决策变量、目标、边界和约束能被明确写出；单位和资源守恒闭合；求解状态可解释。

## Baseline / Primary

规则、贪心或简单分配是 Baseline；LP/MILP/NLP 在规模和假设允许时优先于启发式；GA/SA 通常是 Improved/备选，必须多种子和可行性检查。

## Data / Validation

报告目标值、约束违约/可行率、整数性、最优 gap、运行时间、多初值/多种子、场景损失和实际可执行性。

## Common Misuse

看到“优化”就用遗传算法；把局部/启发式最好解称全局最优；Big-M/罚项无来源；四舍五入后破坏约束。
