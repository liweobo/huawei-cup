# Write Paper

## Purpose

把已验证的模型证据组织为可独立理解、数字一致的竞赛论文。

## Preconditions

至少有明确的方法、真实结果或清晰标记的未运行部分；来源记录可用。

## Required Reads

- [`../rules/evidence.md`](../rules/evidence.md)
- [`../references/innovation-patterns.md`](../references/innovation-patterns.md)
- 声称创新时读取 [`../references/gotchas.md`](../references/gotchas.md) 的 Fake innovation。

## Inputs

题面分析、假设、模型、实验、验证、图表、来源和 Competition State。

## Task Anchor

明确当前写哪个章节、允许改模型与否、需要哪些图表和完成标准。

## Steps

1. 读取 [`../templates/active-evidence-set.yaml`](../templates/active-evidence-set.yaml) 的当前实例和 Evidence Ledger；只从其中选择的 `run_id/experiment_id/artifact_id` 生成论文数字，不扫描整个工作目录。
2. 按问题重述、问题分析、假设/符号、数据、各子问题模型、检验、灵敏度/鲁棒性、评价、结论、引用和附录组织材料。
3. 每个数值 Claim 使用 [`../templates/paper-claim.yaml`](../templates/paper-claim.yaml) 绑定 artifact、JSON path、run ID 和 experiment ID。
4. 每完成模型就同步记录变量、公式、参数来源、算法、结果和局限。
5. 摘要写研究对象、各问题方法、关键真实数字、验证、结论和真正创新；禁用无证据的“效果较好”。
6. 创新点回答原问题、修改内容、合理性、改善位置和实验支持；激活 Fake innovation 检查。
7. 核对摘要、正文、表格、图、代码、单位和 active evidence version；生成的 Paper Claim 必须使 `Claim -> Evidence -> Artifact` 仍可解析。
8. 观察性关联先读取 [`observational-association.md`](../references/observational-association.md)，同时交代分配机制、暴露时序、实体数/观测数、处理前调整依据和 crude / adjusted 结果。Paper Claim 增补 `text` 原句及 association_contract，检查 `UNSUPPORTED_CAUSAL_CLAIM`；使用“与……相关”“调整后仍观察到……关联”。把未知暴露时序、初始测量的时序限制、稀有组和共现措施写入结果解释，不能用统计显著性替换因果识别。

## Checks

每个题目要求是否有结论？每个数字是否来自 ACTIVE_EVIDENCE_SET？是否出现未标记的跨 run 引用？创新是否只是算法名称？

## Outputs

指定章节/摘要、证据引用表、图表清单和待补证据清单。

## Stop Conditions

关键数字无运行记录或引用无法核验时，不把相关段落标为完成。

## Handoff

交给 Reviewer 时附当前版本、代码/结果映射和已知风险。

## Common Failure Modes

最后才写论文；摘要没有数字；符号/单位漂移；把模型名当创新；结论超出验证范围。
