# Feature Engineering Comparison

结论：当前Skill **不是只会直接喂原始字段**。I01/I09/I10已有clinical、volume/location、shape/intensity拼接、血压拆分、fold内预处理，以及first/last/max/change/slope。缺少的是围绕问题结构组织候选表示、保留基线信息并验证特征组增量价值的具体操作过程。

| Feature family | Skill current evidence | Reference evidence | Diagnostic |
| --- | --- | --- | --- |
| Raw / clinical | 病史、年龄性别、血压拆分 | 各篇使用；P03/P07/P10另有分箱 | 分箱不是天然优点，须查信息损失 |
| Volume / ratio / location | 首次HM/ED与部位比例，已join | P05 pp40–42以比例×体积得到区域量；P08 pp12–16左右合并 | 可学习量纲和含义驱动构造；具体脑区合并属G2 |
| Shape / intensity | Q1/Q3a已用表3特征，join覆盖不完整 | P03/P06/P08/P09筛选冗余与相关特征 | 不能把当前差距误写成“缺radiomics”；需要同协议验证保留/筛选 |
| Nonlinear transform / interaction | Q2a z²；Q2c log-time²和time×exposure | P01 onset-delay权重；P10 log-time；P04讨论交互 | 有候选假设价值；复杂度、单位、泄漏和验证先于构造 |
| Temporal change / slopes | Q3b全局slope、first/last/max/change | P01持续时间；P05局部斜率；P06近期加权、IntegratedSlope、末次/max | 当前不是无时间特征，但无法区分某些转折；是否有增益仍未验证 |
| Peak / AUC / curvature | 无完整表示或对照 | 主集合未形成可确认的共同实现模式；P06的IntegratedSlope不是AUC | 不靠预期关键词新增硬要求 |
| Trajectory representation | Q2b只按first ED | P06标准化序列/DTW距离表示；P10阶段斜率三维 | 两篇独立支持，非多数共识；可作为同一特征表示候选 |
| Multimodal fusion | 首次多视图拼接，Q3b未沿用完整Q3a输入 | 8/10明确baseline+followup；P08分域筛选融合；P09基线21+末次105 | **最强直接缺口**：信息丢失和增量混淆，非缺少深度融合网络 |
| Selection / dimension discipline | 简单正则化，已有高维样本检查 | 9/10显式筛选/降维；P07两套筛选×模型 | 说明应比较表示；不证明PCA/MI/grey一定有用 |
| Feature ablation / attribution | 未见持久化输入组对比 | P01 p19；P06 p51；P07 pp47–58；P09 pp59–62 | 4/10有明确输入变体比较；原结果的验证缺点须剥离 |

## Skill实际缺什么，而不缺什么

只读检查 [design-model.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/skill/workflows/design-model.md)、[model-selection.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/skill/references/model-selection.md)、[innovation-patterns.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/skill/references/innovation-patterns.md)、prediction/classification模型族与group-validation。

已有：baseline、最多三个模型族、变量/指标构造可作为创新、同协议比较、fold内选择与聚类。因而“完全没有feature engineering原则”是错误诊断。

未见成形的操作原则：把输入按信息源/时间窗口组成可比较特征集；保留基线后做增量；区分变更表示和变更模型；以简单无收益候选允许被否决的方式完成消融。这一缺口在Q1高维拼接、Q3b丢基线、Q2b只有单一表示中重复出现。**这是对现有宽泛原则的具体化不足，而不是增加模型名目录。**

## 单一未来候选的边界（本轮不实施）

VALIDATION_SAFE_FEATURE_SET_DESIGN_AND_ABLATION：按题意列出基线信息、少量派生表示和预期机制，在同一预测时点/样本/folds/metrics与受控模型下比较基线、基线+候选组、必要的删组。选择只在training/inner folds发生，外层验证不反复调特征。没有收益可保留简单基线。

纵向和多模态只是该原则的验证用例，不同时开发trajectory clustering、multimodal neural fusion、完整robustness或新基础设施。可迁移到设备监测、城市/企业面板、营销/教育行为、实验测量等。
