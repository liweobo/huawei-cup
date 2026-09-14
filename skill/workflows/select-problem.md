# Select Problem

## Purpose

从多道赛题中选择最容易形成完整、可验证建模闭环的题，而不是最好开始的题。

## Preconditions

已取得各题题面、附件概览、比赛规则状态和团队能力信息；未知项可标 `[需要验证]`。

## Required Reads

- [`../rules/competition.md`](../rules/competition.md)
- [`../references/problem-taxonomy.md`](../references/problem-taxonomy.md)

## Inputs

赛题、附件目录、团队数学/编程/领域/写作能力和剩余时间。

## Task Anchor

确认要比较哪些题、需要多快得出结论、哪些专业领域不在本轮调研范围。

## Steps

1. 为每题列出子问题、预期交付物、数据可得性、最小 Baseline 和验证路径。
2. 1–5 分评价题意、数据、数学、编程、专业门槛、文献、创新、可验证性、表达、团队匹配和时间风险；标明高分方向和证据。
3. 比较“最小可交付闭环”和关键路径，识别会阻断后续子问题的最大风险。
4. 给出首选、备选和高风险题，并说明触发换题的条件。

## Checks

评分是否混淆难度与有利程度？是否只因能快速跑模型就推荐？是否有可验证 Baseline？

## Outputs

选题矩阵；首选/备选/高风险题；潜在路线；最大风险；可能卡点；换题条件。

## Stop Conditions

缺少完整题面或关键附件时只给暂定结论；不得伪装成最终选题。

## Handoff

更新 Competition State 的 Selected Problem、P0/P1 Risks 和 Next Highest-Value Action。

## Common Failure Modes

选最熟悉而非最完整的题；把创新空间等同复杂算法；忽略团队和验证成本。
