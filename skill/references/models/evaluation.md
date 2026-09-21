# Evaluation Model Family

## Required Semantic Precondition

在选择或计算任何评价算法前，先完成 [`../evaluation-semantics.md`](../evaluation-semantics.md) 的 Evaluation Target & Output Semantics Contract，冻结评价对象、决策问题、数学输出类型、绝对/相对属性、comparator/threshold provenance 与适用范围、hard-gate 链接和 allowed claim。Contract 未闭合时不进入 weighting、normalization、thresholding、ranking 或 classification。

## Candidates

等权/简单加权、AHP、熵权、TOPSIS、组合权重、稳健排序和非补偿决策规则。

## Fit

有方案×指标矩阵，指标方向、单位、权重语义和补偿性可以解释；如果指标是硬约束，不应只用一个补偿性总分。

## Baseline / Primary

等权或业务规则是 Baseline；AHP、熵权或 TOPSIS 是可比较的权重/排序模块，不是自动创新。主结论必须报告权重/标准化敏感度和排名稳定性。

## Data / Validation

记录指标同向化、标准化、权重来源、冗余处理、新增方案影响和排名变化。对极端值、缺失和零值做明确处理。

## Common Misuse

看到“评价”就套 TOPSIS；先算分再定义分数含义；把相对分数/排名/分位值写成概率或合规；comparator 对象/单位/范围不匹配；双重计权；把离散度等同重要性；不检查排名逆转或硬约束。
