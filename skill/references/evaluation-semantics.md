# Evaluation Target & Output Semantics Contract

## Activation boundary

在综合评价、相对得分、排序/分级、风险指数、阈值评价、法规/标准比较、概率样输出、用于决策的分位数或物理估计，以及 AHP、熵权、TOPSIS、模糊评价或多准则决策中激活本 Contract。普通回归、预测分类、优化目标值和机理参数估计若没有“评价输出 -> 决策/声明”转换，不激活。

在任何 weighting、normalization、thresholding、ranking、classification 或 algorithm selection 前，从 [`../templates/evaluation-contract.yaml`](../templates/evaluation-contract.yaml) 建立：

1. `evaluation_object`：被评价的稳定对象；中途改变对象必须新建输出定义。
2. `decision_question`：输出最终回答的问题。
3. `output_semantics`：`PROBABILITY | QUANTILE | PHYSICAL_ESTIMATE | COMPLIANCE | RELATIVE_SCORE | RANK | CLASS`。
4. `absolute_or_relative`、`output_unit` 与 `output_scope`。
5. comparator/threshold 的值、单位、来源、对象/人口/地域/时间/类别适用范围及版本日期。
6. `hard_gate`：只链接既有 hard-constraint rule，不建立第二套硬约束框架。
7. `allowed_claim` 与机器可核验的 `allowed_claim_semantics`。
8. `status`：`EVALUATION_SEMANTICS_VERIFIED | PARTIAL | UNVERIFIED`。

只有 target、output、comparator 和 claim 闭合时，正式评价结论才能为 `VERIFIED`。

## Semantic rules

- 只有真正的 `P(event)` 或有独立校准模型与证据的转换输出才是 `PROBABILITY`。TOPSIS closeness、AHP/熵权分数、模糊隶属度、归一化指数、排名百分位和阈值比默认都不是概率。
- `Q_p(X)` 是与 `X` 同单位的分位值；`p` 是 CDF 概率水平。二者都不等于“安全概率”。
- `RELATIVE_SCORE` 只在声明的 comparison set/normalization scope 内解释；`RANK` 只表示相对顺序。二者不得自动升级为绝对质量、绝对风险、概率或合规。
- `CLASS` 的边界必须有 `PROBLEM_GIVEN | OFFICIAL_STANDARD | EXTERNAL_REFERENCE | DERIVED | ASSUMED` provenance；无来源只能标 `ASSUMED`，不能冒充官方分级。
- `COMPLIANCE` 需要输出与 comparator 在数学对象、单位、population、geography、time、category/outcome、标准适用性和 version/date 上可比。单位可换算不等于对象可比；dietary intake 不能仅靠数字或单位变换与 blood concentration 或 food-content concentration 比较。
- `rho=q/T` 的 `rho=1` 可标 `DERIVED`，但必须先验证 `q` 与 `T` 语义可比。
- current-set min-max、TOPSIS ideal point 等候选集依赖输出必须标 `RELATIVE`，并披露增删 alternative 可改变全部分数。
- 合法的 score -> probability 转换必须把 calibration model、证据和 `VERIFIED` 状态记录为新的数学步骤；不能只换标签。

## Forbidden claim promotion

没有新的、独立数学映射和证据时，禁止：

- `RELATIVE_SCORE/RANK/FUZZY_MEMBERSHIP -> PROBABILITY`；
- `RELATIVE_SCORE/RANK -> COMPLIANCE`；
- `QUANTILE -> PROBABILITY`；
- `PHYSICAL_ESTIMATE -> COMPLIANCE`（除非 comparator contract 完整且兼容）。

`allowed_claim` 必须限定最终文字，例如“当前六城市中的相对排名”不能写成“绝对城市质量”；synthetic calibration test 不能写成真实总体概率。

## Reviewer guards

使用 [`../scripts/evaluation_semantics.py`](../scripts/evaluation_semantics.py) 做确定性结构/语义检查：

- `EVALUATION_TARGET_UNDECLARED`
- `OUTPUT_SEMANTICS_UNDECLARED`
- `RELATIVE_OUTPUT_AS_PROBABILITY`
- `QUANTILE_PROBABILITY_CONFLATION`
- `RELATIVE_OUTPUT_AS_COMPLIANCE`
- `COMPARATOR_SCOPE_MISMATCH`
- `THRESHOLD_PROVENANCE_MISSING`
- `EVALUATION_CLAIM_SCOPE_EXCEEDED`

helper 不实现 AHP、TOPSIS、熵权、模糊评价、概率校准、风险估计或法规检索。`COMPARATOR_SCOPE_MISMATCH` 阻止正式 compliance/probability 升级；若 hard safety/legal/feasibility threshold 被违反，由既有 hard-constraint rule 判定失败，软总分不能补偿。
