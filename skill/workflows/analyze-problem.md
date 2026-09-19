# Analyze Problem

## Purpose

把题面转成可验证的子问题、变量、约束和依赖关系。

## Preconditions

已有完整题面；若题面缺页、公式损坏或附件未到，先记录阻塞。

## Required Reads

- [`../rules/modeling.md`](../rules/modeling.md)
- [`../references/problem-taxonomy.md`](../references/problem-taxonomy.md)
- [`../references/ordinal-modeling.md`](../references/ordinal-modeling.md)（目标是等级标签时）
- [`../references/group-validation.md`](../references/group-validation.md)（存在重复实体或纵向观测时）
- [`../references/mechanism-closure.md`](../references/mechanism-closure.md)（存在机制、物理或动态模拟子问题时）

## Inputs

题面、附件说明、已知规则和当前 Competition State。

## Task Anchor

明确本轮拆哪几个子问题，以及输出是分析表、依赖图还是可执行建模计划。

## Steps

1. 对每个子问题写：要求、输入、输出、已知量、未知量、显式/隐含约束、时间/空间关系。
2. 区分题面事实、合理假设和待验证推断，记录变量单位和索引。机制/物理/动态子问题同时建立 Mechanism Closure Contract，逐项登记适用的几何、初始状态、边界/接口、forcing、材料定律、观测条件和终止条件；缺失 essential input 时不要静默补值。
3. 依据目标、变量、约束和随机性标注一个或多个问题类型；分类目标同时区分 nominal 与 ordinal。只有题面、数据字典或明确声明给出等级顺序时，才记录 `ordered_levels` 和 `ordering_source`。
4. 识别可能的 entity key 和重复观测，明确最终泛化到新记录、新实体还是实体未来时间；记录 `validation_unit`，不要默认按行切分。
5. 生成 Problem Dependency Graph，注明每条边传递的数据、参数或决策。
6. 为每个子问题定义最小交付物、Baseline、验证方式和论文位置。机制子问题额外给出 closure status 和 allowed claim level。

## Checks

输入输出是否明确？依赖是否会传播误差？题目每个动词是否都有对应产出？

## Outputs

子问题表、变量/约束表、依赖图、类型判断、关键路径和待验证清单。

## Stop Conditions

输入、输出或核心约束仍不明确时，不进入正式模型选择。

## Handoff

把每个子问题状态和下一动作写入 Competition State。

## Common Failure Modes

按关键词分类；遗漏隐含可行性条件；后续问题使用前一结果却未记录误差传播。
