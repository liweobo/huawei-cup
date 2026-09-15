# Generalizable Gaps — one recommendation

**Decision: GENERALIZABLE_GAP_FOUND**

**Top-1: VALIDATION_SAFE_FEATURE_SET_DESIGN_AND_ABLATION**

中文：在合法验证内设计特征组，并验证筛选、变换与新增信息的增量价值。

这是对当前已展示建模过程的诊断，不是从一道题证明Skill永久不会做特征工程。它也不是“Logistic不如XGBoost”或“获奖论文用LSTM所以必须加LSTM”。

## Classification

| Category | 发现 | 证据与处理 |
| --- | --- | --- |
| G1 — Generalizable Skill Gap | 缺少任务对齐的特征组设计、保留共同基线的增量比较，以及fold内特征筛选的实际消融证据 | I01/I09/I10；Q3b删掉Q3a首次影像视图；B07/B08显式讨论维度/特征比较，B03保留静态信息融合随访。唯一Top-1 |
| G2 — Problem-Specific Improvement | 本题4名48h无随访者的标签可观测性说明、流水号异常、HM–ED特定关系与临床特征含义 | I04/I05与B08 pp.7–8；应在本题新分析中补充，不改冻存标签。本轮不提医学专用模块 |
| G2 — Problem-Specific Improvement | 补齐本题Q3c因素表、完整九问叙事和最终论文；记录Q1/Q3升级指标缺少持久副本 | I09/I10只打印stdout、I12/I14明确诊断阶段。是本次交付/证据缺项；不能据此直接认定需要新增解释算法或修改write-paper |
| G3 — Reference Difference Only | Logistic/ordinal vs RF/NN/DeepForest；单条二次 vs Gaussian/混合模型；是否使用propensity | 没有同数据/同目标/同split可比结果，不能按模型名认定落后 |
| G3 — Reference Difference Only | 完整trajectory clustering、DTW、functional clustering、growth mixture作为必修能力 | B01/B04/B08主要静态分组；B03对齐/表示不明；B07多维含变化量而非可靠完整形态分组。当前baseline有局限，但参考不足以把特定轨迹算法列为优先缺口 |
| G3 — Reference Difference Only | ACF/PACF、复杂动态HM→ED模型、更多校准/敏感性图 | 未见可信滞后识别或同协议收益。校准、uncertainty/robustness仍是已知不足，本轮证据不足以改排为新的Top-1；本轮不实施 |
| G4 — Reference Weakness | 全量SMOTE/PCA/缩放先于切分；训练拟合被当验证；簇数反复在全体数据择优 | B03 Q1源码；B07 Q2/Q3源码。原文/代码证据定位见source-notes |
| G4 — Reference Weakness | 不核实治疗时序/混杂便声称“治疗有效/有害”，importance外推临床因果 | B01/B02/B03/B04/B07/B08都有不同程度问题；Skill纪律应保留 |
| G4 — Reference Weakness | 48.90h改48h、遗漏6mL或发病偏移、残差口径/指标名混淆、奖级未经证实 | B08 pp.7–8，B02 pp.3–5，B07 Q2b代码；来源台账严格区分奖项身份与方法质量 |

G3表示“本轮没有证据仅因方法不同认定通用缺口”，不表示现有所有模型已经最优。Q2b的表示不足作为G1的一个实例保留，但不扩展成第二个模块。

## Top-1 dossier

- **gap_name:** VALIDATION_SAFE_FEATURE_SET_DESIGN_AND_ABLATION
- **evidence:** 当前Q1/Q3a已有临床、体积/位置、形状/灰度，但定向比较主要改变模型/类别权重/ordinal形式，没有保存特征组贡献或筛选收益；Q3b改为clinical+体积聚合，没有延续Q3a完整首次影像矩阵，因此既有Q3a→Q3b分数变化同时含新增与删除信息；Q2b只用首次ED一维分组，没有多维表征比较。
- **reference_support:** R-B07原文L943–964明确all features vs top10；R-B08 PDF pp.8–10、31–35说明小样本高维/共线性及特征筛选；R-B03 L968明确保留静态视图再加入时序视图。这些来自多个独立公开方案。其成绩不具可比性，所以只支持建模思想的重要性，不支持其数值或具体筛选规则。
- **why_generalizable:** 小样本多变量、不同来源特征融合、随访/阶段数据带来的增量比较，常见于设备状态、城市经济、用户行为、政策/教育、实验科学。变量数量、冗余和可得时间会影响泛化、解释和稳定性；无需临床字段名也能定义和验证。
- **why_current_skill_is_insufficient:** 现有Skill已经要求预处理/特征选择在fold内、模型比较同协议；并非没有安全规则。问题是缺少将原始字段转化为少量有任务理由的候选表示、保持共同特征基线、用可追溯消融判断收益的操作深度；本题实际产物反复停在拼表/简单汇总。纯容量控制与更严格切分不能替代对信息表示的比较。
- **recommended_next_phase:** 仅研究并验证上述一项能力；保留原始baseline，在同一合法预测场景、实体集合、cutoff和fold下，比较少量有解释的特征组及fold内缩减方案，保存组贡献和失败结果。先验证设计能识别冗余/遗漏信息，再做小范围真实题定向对照；无增益时应保留简单模型。
- **claim_limit:** 本轮没有训练或消融，不能保证未来指标提高，也不能称当前方案已被某获奖模型数值击败。缺口结论置信度MEDIUM；它足以支持下一阶段的受控验证，不支持直接加入任何参考算法。

## 为什么它排在第一

1. 同时影响Q1概率预测、Q3有序预测和Q2分组的建模质量；已有数据都能利用。
2. Q3b的共同基线缺失是确定性证据，Q1/Q3的特征比较空白能从现有测试/产物核实。
3. 跨领域价值明确，且可以在已有Temporal/Group/Ordinal/Imbalance规则下真实验证。
4. 不依赖单篇论文、不依赖奖级、不依赖不可比高分；B07/B08侧重筛选，B03侧重多视图保留，指向同一信息表示问题。
5. 相比直接建轨迹聚类、因果ML或更多优化算法，问题范围更清楚；本轮没有可靠证据将后者列为首选。

## Stop boundary

本轮只生成独立对标artifact。没有改Skill、routing、历史结果，也没有实施任何上述建议；不会自动进入下一阶段。
