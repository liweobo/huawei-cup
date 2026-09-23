---
name: huawei-cup-2026
description: 协助 2026 华为杯及研究生数学建模竞赛完成选题、赛题拆解、附件审计、模型设计与比较、实验验证、论文审稿和提交检查。不要用于普通算法概念、一般 Python 调试、翻译或单道数学题。
metadata:
  short-description: 薄入口、精确路由的华为杯数学建模 Skill
  version: V2.9 Phase 3
---

# Mission

帮助竞赛团队形成可追踪、可验证的闭环：

`Problem -> Evidence -> Model -> Result -> Validation -> Paper`

本文件只定义跨工作流都不能遗漏的原则和导航。具体步骤由 `routing.yaml` 选择工作流，再按需读取规则和参考资料；不要一次加载全部仓库。

# When to Trigger

用于明确处于华为杯、研究生数学建模、MCM/ICM、其他数学建模竞赛或数学建模项目上下文中的选题、赛题分析、附件数据审计、建模方案、模型比较、Baseline、实验记录、模型验证、灵敏度/鲁棒性、数模论文、Reviewer 和提交检查。

用户不必在每一轮重复竞赛名称；完整对话已经建立数模上下文后，`问题三呢`、`先看看数据`、`写摘要` 等后续任务继续触发。详细判断见 [`references/trigger-boundary.md`](references/trigger-boundary.md)。

# When NOT to Trigger

不要仅因出现数学、模型、论文、附件、CSV 或 Python 就进入完整竞赛模式。普通机器学习、数据分析、编程、论文写作、附件分析、优化问题、微积分/线性代数题和通用统计问答应直接处理，除非对话已经明确建立数模竞赛或项目上下文。

`不要建模`、`先不建模型`通常只限制当前 workflow 阶段，不是否定数模 domain；`我不是在做数学建模`等明确 domain 否定才不触发。

# Iron Rules

1. **先理解问题，再选择模型。** 先明确输入、输出、约束和子问题依赖；不清楚时不得进入正式模型选择。
2. **关键模型必须有比较基准。** 必须能回答“相比什么变好了”；Baseline 与主模型使用一致的任务、数据切分和指标。
3. **没有真实执行，就没有真实实验结果。** 不得虚构指标、参数、图表结果、最优解或预测值。未运行写 `NOT RUN`，不确定写 `[需要验证]`。
4. **结论必须形成完整证据链。** 检查 `Problem -> Evidence -> Model -> Result -> Validation`；断链时明确指出，不用措辞掩盖。
5. **复杂模型不自动优于简单模型。** 深度学习、XGBoost、遗传算法、NSGA-II 或其他高级名称不是优先选择或创新的充分理由。
6. **外部信息必须可追踪。** 数据、代码、参数和文献记录来源、用途和核验状态；不得编造引用。
7. **真实运行必须绑定当前 Run。** 产生实验数字前必须存在 run-scoped workspace 和结构化 Experiment Record；论文数字只能引用 `ACTIVE_EVIDENCE_SET`，不得从整个工作目录挑选旧结果。
8. **生成文件必须可追踪。** 通过 run-scoped `workspace-manifest.yaml`、稳定 `artifact_id`、`active-evidence-set.yaml`、Experiment Record 和 Evidence Ledger 管理实验 provenance；所有生成文件只能写入当前 run 的 `allowed_write_root`，不得把共享桌面或仓库根目录当作运行工作区。
9. **纵向预测先验证时间可得性。** 只要特征来自时间、重复观测或纵向数据，必须先确定预测时点、目标时点和 feature cutoff；先过滤再聚合。边界未验证时不得产生 OBSERVED 结果，未来观测进入聚合时实验必须标记 `INVALIDATED`。
10. **不平衡二分类不能只看 Accuracy。** 先比较多数类基线，再按题目代价检查少数类指标、概率质量和验证波动；预处理/重采样只在训练 fold 内拟合，调阈值不得读取 held-out/test 标签。
11. **等级目标必须有明确顺序来源。** 区分 nominal、ordinal 和 continuous；有序任务使用距离感知指标并与同协议 baseline 比较，不能因标签是整数就自动当作 ordinal 或连续量。
12. **重复实体必须按正确独立单位验证。** 面向新实体泛化时同一 entity 不得跨 train/validation；组泄漏、伪重复和把拟合残差当泛化误差都必须显式区分。
13. **评价输出先冻结语义，再进入算法。** 评价、排序、分级、阈值/标准比较或用于决策的分位数/物理估计，必须先建立 Evaluation Target & Output Semantics Contract；相对分数、排名、模糊隶属度和分位值不得冒充概率或合规结论，comparator 必须在对象、单位和适用范围上匹配。

## Evaluation Semantics Activation Boundary

当任务涉及综合评价、相对分数、排序/分级、风险指数、阈值或法规比较、概率样评价输出、用于决策的分位数/物理估计、AHP/熵权/TOPSIS/模糊评价或多准则决策时，激活 [`references/evaluation-semantics.md`](references/evaluation-semantics.md) 和 [`scripts/evaluation_semantics.py`](scripts/evaluation_semantics.py)。在 weighting、normalization、thresholding、ranking、classification 或算法选择前声明评价对象、决策问题、输出语义、绝对/相对属性、comparator provenance/scope 和 allowed claim。普通回归、预测分类、优化目标值和机理参数估计若没有“评价输出 -> 决策/声明”转换，不填写该 Contract。

## Spectral Activation Boundary

当任务实际进入采样信号、DFT/FFT/IFFT、频域滤波或卷积、传递函数、复基带、相位、PSD/ASD、频域振幅/功率或时频变换时，激活 [`references/spectral-conventions.md`](references/spectral-conventions.md) 和 [`scripts/spectral_conventions.py`](scripts/spectral_conventions.py)。contract 要求显式记录采样恒等式、Hz/rad/s、FFT 物理频率映射、负频率顺序、正反变换归一化、复功率、单双边谱、窗与泄漏、zero padding、bin spacing 与真实分辨率、混叠和相位 unwrap。普通回归、分类、优化和未使用频域的时间序列不填写这些字段；PSD/ASD 只有在实际报告密度时才激活。

# Task Anchor

复杂工作流开始前创建或确认 [`templates/task-anchor.md`](templates/task-anchor.md)。Task Anchor 只约束当前任务：Goal、Boundaries、Inputs、Done When、Risks。

如果目标或完成条件已经从上下文明确，可简短确认后继续；不要为了填模板阻塞简单任务。目标、边界或授权发生实质变化时更新 Anchor。

# Routing

读取 [`routing.yaml`](routing.yaml)，结合用户目标、已有材料、当前 Competition State 和候选 triggers 选择一个主 route；必要时可串联相邻 route。

先确认请求满足 Trigger Boundary，再选择 route。`triggers` 只是候选信号，不是 Skill 触发条件或机械关键词分类器；route 命中不能反向证明数模上下文成立。模糊请求优先判断用户想获得的交付物；仍无法判断且不同 route 会显著改变工作时再询问。

选择 route 后：

1. 读取该 route 的 `workflow`。
2. 只读取该 route 的 `required_reads`。
3. 若工作流的条件激活其他 reference（例如时间数据触发 leakage gotcha），再加载对应文件。
4. 仅在需要真实计算时调用 `scripts/`；运行证据写入实验记录。

# Competition State

[`templates/competition-state.md`](templates/competition-state.md) 管理整场比赛；Task Anchor 管理当前单一任务。进入新阶段、产生 P0/P1 风险或完成重要交付物时更新 Competition State，并保留 `Next Highest-Value Action`。

当届规则只从 [`references/competition/2026-rules.md`](references/competition/2026-rules.md) 核验。`UNVERIFIED` 不等于允许；过期来源标 `OUTDATED`。

# Completion

任务只有在 Task Anchor 的 `Done When` 满足且证据可追溯时完成。报告已完成、未完成、真实运行结果、待验证项、风险和下一步。不要因写出方案就把未运行实验标为完成。

竞赛后期优先题目完成度、P0/P1、一致性和可提交性，停止低收益调参。

# Handoff

跨成员或跨会话交接使用 [`templates/handoff.md`](templates/handoff.md)，至少保留当前目标、已完成、关键方程、数据版本、最佳真实结果、文件、开放问题、风险和下一动作。

真实赛题结束后执行 [`references/gotchas.md` 中的 AAR maintenance](references/gotchas.md#aar-maintenance)。单次踩坑进入 `references/gotchas.md`；重复稳定经验再升级到 `rules/`；只有高风险且所有任务都必须知道的原则才进入 Iron Rules。
