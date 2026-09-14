# Observational Treatment / Intervention Association

当题目要求分析 treatment、intervention、policy 或 action 与 outcome 的关系时使用。字段名不能证明随机分配，也不能证明变量在干预前已知。本协议适用于临床随访、政策、营销、教育、维修和风控等非随机措施。

## Association Analysis Contract

在计算或解释组间差异前，用 [`association_analysis.py`](../scripts/association_analysis.py) 的 `build_association_contract()` 记录：

| 字段 | 内容 |
| --- | --- |
| `exposure` | 一个或少量明确的措施变量；定义 0/1、记录期间及对象单位 |
| `outcome` | 结局、单位、测量窗口；不能同时作为解释变量 |
| `assignment_type` | `RANDOMIZED` / `OBSERVATIONAL` / `UNKNOWN`，以设计证据确定 |
| `exposure_time_known` | 实际暴露/分配时间是否可确认；不能凭首次观测时间猜测 |
| `candidate_confounders` | 每项的 name、`temporal_role`、evidence；可附 available_at / exposure_at |
| `post_exposure_variables` | 响应、随访测量、结局衍生量等不能当作普通混杂变量的字段 |
| `group_structure` | 已核验的 [Group Structure Contract](group-validation.md)，同时保留行数与实体数 |
| `temporal_structure` | 时间用途、已知坐标/信息边界及 evidence；未来特征检查不能豁免 |
| `estimand` | 具体比较什么：人群、单位、时间点、差值/轨迹差异及条件变量 |
| `claim_level` | `DESCRIPTIVE_ASSOCIATION` / `ADJUSTED_ASSOCIATION` / `CAUSAL_EFFECT` |

`OBSERVATIONAL` / `UNKNOWN` 默认只允许前两级。风险/需求更高的对象可能更容易接受措施，也更容易出现较差结局，即 **confounding by indication**；接受组和未接受组的差异不能直接解释为措施造成的差异。

`CAUSAL_EFFECT` 需要另有已核验的识别设计。本能力不建立该设计：随机分配须有分配与时序核验，非随机设计须有独立识别审查；`causal_identification` 记录 strategy、review_status、evidence_refs、assumptions、temporal_order_verified，随机设计另有 randomization_verified。脚本只接受 `RANDOMIZED_ASSIGNMENT` 或 `EXTERNALLY_IDENTIFIED_DESIGN` 的明确审核记录，不把 regression / matching / IPTW 成功当作识别证据。

## Confounder and exposure timing

- 用于 adjustment 的字段必须是 `PRE_EXPOSURE`，有可追溯证据；字段名含 baseline/initial 不构成证据。只有预先存在的人口属性、历史、严重程度或初始测量，且其处理前属性已确认，才可作为候选。
- `POST_EXPOSURE` 响应/影像/随访结果不能作为普通 confounder；`UNKNOWN` 时序的初始测量也不得擅自加入 adjustment。软件支持该回归不代表调整合法。
- available_at / exposure_at 存在时，通过 Temporal Availability Gate 复核；错误标成 PRE_EXPOSURE 不能覆盖相反的时间戳。结局及其衍生量禁止进入 propensity/treatment-model features。
- 暴露实际时间未知时标 `EXPOSURE_TIME_UNVERIFIED`，仍可做限定清楚的观察性描述与关联；不能声称干预后轨迹发生了因果变化，不能把 episode-level / ever-exposed 标记当作每个观测时点的实时暴露状态，更不能用于其可得时点之前的预测。
- 若题意专门研究多个测量与措施的联合关系，可单列 `joint_variables`，声明 `JOINT_ASSOCIATION_VARIABLE`、同次/更早结局时间的可得性证据及相对干预时序限制。它们属于联合条件描述，不能改名后冒充处理前 confounder；包含潜在响应/中介时不能解释为总效应或直接效应。

## Describe, then compare crude and adjusted associations

先用 `audit_exposures()` 输出接受/未接受/缺失暴露的**实体数**、prevalence、初始特征、结局摘要、co-occurrence 和高度相关措施。重复结果可按每实体的观测均值汇总，必须明确权重与单位。描述初始测量时，同时注明其是否已验证为干预前信息。

任一组支持很少时标 `ESTIMATE_UNSTABLE`；默认每侧少于 10 个实体仅是可配置的审查阈值，不是超过阈值就能稳定推断。缺失暴露不能改成 0；一实体的暴露会变化时，先定义时变问题，不能静默取 first/last。

至少报告两个在**相同完整病例、相同结局与时间基准**上的模型：

1. Crude：`outcome ~ exposure`；纵向任务可共享 time 基函数，并按定义加一个 `time × exposure`。
2. Adjusted：加入少量有处理前依据的 confounders。完整病例过滤对两模型一致，记录被排除的行/实体；学习型插补若用于预测验证，必须在 training fold 内。

系数或方向明显变化，说明可能存在混杂或模型设定影响；写“调整后关联减弱/变化”，不写“治疗效果变弱”。调整不能保证已控制所有混杂。多措施并存时，分别拟合的关联可能反映共同用药/共同措施，不能据此隔离单项贡献或排序。

小样本优先简单、低维、可解释的设定；在看到结局关联前确定少量调整项、时间基函数与措施选择规则。不要巨大组合搜索、大量交互或用高容量重要性排序代替关系分析。探索性的多项 nominal 区间不等于同时置信区间或确证性发现。

## Longitudinal estimation and validation

重复观测可用 mixed model、GEE、按 entity 聚类的回归不确定性，或每实体一行的合法轨迹摘要。有效独立样本数更接近实体数。`time × exposure` 描述组间轨迹差异；时序/识别不支持时只称 `TRAJECTORY_ASSOCIATION`。

`fit_crude_adjusted_association()` 是一个可选简单实现：固定的一次/二次时间项、每措施至多一个线性时间交互、equal-entity WLS、CR1 cluster sandwich 与 t(G−1) nominal 区间；不做模型搜索或自动插补。它拒绝秩亏设计和不足的独立实体数，输出实际分析 IDs、缺失排除、参数数、支持度、粗/调整后估计及区间。

**按实体处理估计依赖，不等于已经完成新实体预测验证。** 预先指定的关联估计可以不产生预测分数；若要选模型或声称新实体泛化，仍须单独执行 GroupKFold/等价协议，记录真实 split IDs，overlap=0。时间外推另过 Temporal Gate，预处理在 training fold 内。`FIT_RESIDUAL` 不得当成 `VALIDATION_ERROR`。若采用 bootstrap，优先抽整个实体。

## Optional propensity methods

不默认使用 propensity score / IPTW / matching。只有暴露定义、处理前协变量、样本量和 overlap 支持时才考虑；否则优先透明的 covariate-adjusted association。

使用时，记录 treatment-model 的实际 feature names，禁止 outcome、结局衍生量、未来信息或处理后普通 confounders。`propensity_diagnostics()` 在每实体一行的表上检查：

- propensity 在 (0,1)，两组 common support 及覆盖比例；不重叠为 `PROPENSITY_OVERLAP_FAILURE`，不可发布有效加权比较；共同取一个内部概率如 0.5 本身不构成失败。
- 权重最大值、极端权重数和每侧/总体 ESS：`(sum w)^2 / sum(w^2)`。极端权重、低 ESS 明确提示不稳定；不能不披露地截权。
- 同一处理前变量的加权前/后 SMD；有残余不平衡需报告，不能只说软件成功。简单范围重叠不证明多维 positivity 或无未测混杂。

这些诊断不建立因果识别，也不自动改变 claim level。本脚本不拟合 propensity、matching 或自动选择权重。

## Experiment and Reviewer gates

Experiment Record 的 planned/executed protocol 标 `association_analysis: true`，经 `apply_association_gate()` 记录 contract、实际 adjustment、实体 IDs 和 dependence handling，再由 `runtime_provenance.validate_experiment_record()` 复核。契约缺失、处理后调整、outcome/future leakage、无依赖处理或不支持的因果等级会阻止 OBSERVED；已有 Group / Temporal 失效原因必须保留。

`review_association_claim()` 辅助捕捉“导致”“使得”“有效降低”“增加风险”和常见英文因果表达；Paper Claim 增补 `text` 原句和 association_contract 后接入现有 claim validator，不能用空原句冒充措辞审核。观察性设计没有独立可靠识别时，Reviewer 报 `UNSUPPORTED_CAUSAL_CLAIM` 并使该 Claim `INVALIDATED`。推荐“与……相关”“调整后仍观察到……关联”“提示可能存在……关系”。词法检查不覆盖所有转述、图注或隐含建议，Reviewer 必须结合上下文与识别证据逐条审核。
