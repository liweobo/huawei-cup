# Final Check

## Purpose

在提交前确认题目完成度、数学/数据/代码一致性、验证证据和规则状态。

## Preconditions

已有接近提交的论文、附件代码/数据清单和当届合规记录。

## Required Reads

- [`../rules/competition.md`](../rules/competition.md)
- [`../references/competition/2026-rules.md`](../references/competition/2026-rules.md)

## Inputs

最终论文、代码、图表、结果、来源、提交要求和 Competition State。

## Task Anchor

限定检查版本和截止时间；此阶段默认不做低收益重构或模型调参。

## Steps

1. 检查所有子问题、关键结论、变量、公式、单位、数据来源和预处理。
2. 检查泄漏、Baseline、验证、灵敏度、鲁棒性、优化可行性和失败边界。
3. 逐项比对摘要、正文、表格、图和代码的数字与版本。
4. 核验 Active Evidence Set、Evidence Ledger、Experiment Record、Paper Claim 和 Reviewer Report 的引用图与 SHA256；broken reference 时不得 READY。
5. 核验文献、外部程序和 `references/competition/2026-rules.md` 的状态、来源和更新时间。
6. 按 P0/P1/P2 给出 READY/NOT READY、必须修复、建议修复和可暂缓项。
7. READY gate 必须读取所有 required questions、正式提交附件、完整论文和 compliance 状态；局部 Q1/Q2 高质量证据不能覆盖 Q3/Q4/Q5 或其他必答项未完成。

## Checks

任何 P0、未回答子问题、关键规则 UNVERIFIED 或数字冲突都不得判 READY。

## Outputs

SUBMISSION STATUS、P0/P1/P2、READY/NOT READY 和修复顺序。

## Stop Conditions

发现 P0 时停止美化，优先修复或明确阻塞。

## Handoff

最终责任人获得唯一提交版本、文件清单、Evidence Ledger、校验状态和剩余风险。

## Common Failure Modes

误把“文件齐全”当“内容完成”；规则沿用旧年份；摘要数字与正文不一致。
