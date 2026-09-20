# Audit Data

## Purpose

确认附件的结构、质量、时间因果关系、单位和 Data → Problem Mapping。

## Preconditions

能够读取原始文件；不直接覆盖原文件。

## Required Reads

- [`../rules/evidence.md`](../rules/evidence.md)
- [`../references/gotchas.md`](../references/gotchas.md)
- [`../references/imbalanced-classification.md`](../references/imbalanced-classification.md)
- [`../references/ordinal-modeling.md`](../references/ordinal-modeling.md)（发现有序候选标签时）
- [`../references/group-validation.md`](../references/group-validation.md)（发现重复实体或纵向记录时）
- [`../references/spectral-conventions.md`](../references/spectral-conventions.md)（附件是采样信号或包含频域量时）

## Inputs

CSV 或 `.xlsx`、字段说明、题面、标签定义和预测/决策时点。当前版本不承诺旧式 `.xls`。

## Task Anchor

明确审计哪些文件、服务哪些子问题、是否只做只读报告。

## Steps

1. 运行 `scripts/data_audit.py` 辅助获取文件、Sheet、字段、类型、样本、缺失、重复、唯一值、统计量、IQR 异常候选、ID/常量候选、类别分布、高相关候选和时间顺序提示。
2. 建立 Data → Problem Mapping：含义/单位、来源、子问题、角色、预测时是否可得、缺失处理和风险。
   采样信号或频域附件同时登记 Fs、dt、样本数、物理频率单位、目标带宽和 aliasing 风险；没有确认的 Fs 不得静默生成物理频率轴。
3. 激活 Gotchas：任务涉及时间可得性、未来预测或纵向聚合时，必须建立 Temporal Availability Contract，明确 `prediction_as_of_time`、`target_time` 和 `allowed_feature_horizon`。先过滤超过边界的观测，再允许构造任何 longitudinal aggregate；边界不能确定时标 `UNVERIFIED` 并停止正式实验。静态重复测量另查 group 结构，不因重复本身推定时间预测；纯描述曲线需说明 time 是已知坐标及不存在未来依赖特征。分类标签存在时检查类别分布；二分类明显不平衡时读取 [`imbalanced-classification.md`](../references/imbalanced-classification.md)，记录多数类基线和正类流行率。疑似有序标签时用 `scripts/data_audit.py --ordinal-context` 建立 Ordinal Target Contract；没有明确顺序来源时保持 `UNVERIFIED`。审计提示不等于自动删类、重采样或确认标签类型。
4. 自动检查 identifier 候选与一实体多记录结构，使用 `--group-context` 确认 `entity_key` 和 prediction setting（同实体新记录 / 新实体 / 同实体未来 / 新实体未来）。建立 [Group Structure Contract](../references/group-validation.md#group-structure-contract)，记录实体数、行数、每实体行数的 min/median/max、`repeated_entities`、`validation_unit` 和 `unit_of_analysis`；候选统计照常输出，key 或场景不明确则保持 `UNVERIFIED`。不能默认 ROW；静态重复测量不因重复本身而凭空要求时间字段。一实体一行的聚合表仍记录来源及跨实体、时间和预处理检查。
5. 措施/干预关系题先读取 [`observational-association.md`](../references/observational-association.md)，建立 Association Analysis Contract，核验 assignment_type、exposure timing、处理前 confounder 证据、结局与 claim_level。用 `association_analysis.audit_exposures()` 描述实体级接受/未接受/缺失暴露数、初始特征、结局、prevalence、co-occurrence 和稀有/高度相关措施。初始测量不自动属于处理前信息；时间无法确认标 `EXPOSURE_TIME_UNVERIFIED`，仍可进行限定范围的关联分析。
6. 识别标签后验字段、ID 代理、全量预处理、单位冲突、重复样本和异常值语义。如果数据服务机制/物理/动态模型，按需读取 [`../references/mechanism-closure.md`](../references/mechanism-closure.md)，把材料参数、forcing、观测位置和数值终止输入分别标记为 GIVEN、DERIVED、EXTERNAL、ASSUMED、PARAMETERIZED 或 MISSING；数据审计不能替模型静默补齐缺失 closure。
7. 先形成 Canonical Data Audit Summary，再输出自然语言结论；所有最终数字必须来自同一份 summary。
8. 区分观测事实、风险提示和拟议清洗；每次转换进入实验记录。

## Canonical Data Audit Summary

至少维护以下字段，并让报告、证据台账和后续回答引用同一份记录：

```yaml
data_audit:
  total_rows:
  missing_cells:
  invalid_rows:
  duplicate_full_rows:
  frequency_boundary_rows:
  anomaly_rows:
  unresolved_questions:
```

同一 canonical metric 在一次 response 中出现相互矛盾的值（例如
`duplicate_full_rows: 0` 和 `duplicate_full_rows: 1`）时，必须标记为
consistency failure，不能用后续扫描结果静默覆盖前文。

### Temporal Availability Contract

纵向预测必须在特征工程前填写以下契约：

```yaml
task:
entity_key:
target:
target_time:
prediction_as_of_time:
allowed_feature_horizon:
time_column:
aggregation_required: true
post_horizon_records:
status: PASS  # PASS / FAIL / UNVERIFIED
```

`allowed_feature_horizon` 是题目允许的信息上界与预测时点的较早者。调用
`scripts/temporal_availability.py` 的 `filter_before_aggregation()` 后，才能生成
`last`、`max`、`mean`、`slope`、`change`、rolling 或 cumulative 特征。任何超过
cutoff 的观测进入聚合都会使实验 `INVALIDATED`；被排除的行数和受影响实体数要写入报告。

多源、多阶段或高维输入时按需读取 [`feature-set-design.md`](../references/feature-set-design.md)，建立 Feature Set Contract；按来源/语义/时间组织信息组，列明合法 baseline、候选增量组、实际列、派生公式、可用时点与排除理由。字段数/样本数及各组缺失覆盖进入审计。

## Checks

missing / duplicate / outlier 是否复核？时间顺序与 leakage 是否检查？是否把 ID、类别或相关性候选当成自动删除指令？单位和时间频率是否一致？

## Outputs

数据审计报告、字段映射、泄漏/单位/异常风险和下一审计动作。

## Stop Conditions

字段含义、标签时点或单位会改变模型结论但尚未确认时，停止正式实验并标 `[需要验证]`。

## Handoff

记录原始文件版本、审计命令、报告路径和未解决风险。

## Common Failure Modes

自动删异常；将编码字段当连续量；先全量标准化再切分；时间序列随机切分。
