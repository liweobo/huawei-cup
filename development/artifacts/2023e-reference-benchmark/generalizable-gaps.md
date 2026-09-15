# Generalizable Gaps

**Final decision: GENERALIZABLE_GAP_FOUND**

只确认一个G1并作为Top-1。其他差异分别属于题目改进、方法不同、参考缺陷或当前run完成度问题；本轮不实施。

## G1 — VALIDATION_SAFE_FEATURE_SET_DESIGN_AND_ABLATION

- gap_name: VALIDATION_SAFE_FEATURE_SET_DESIGN_AND_ABLATION
- 中文：有验证依据的特征集设计与增量消融。
- evidence: 冻结摘要I01/I09/I10：Q1/Q3a已有多视图，但没有保存特征组比较；Q3b未合并Q3a的完整首次shape/intensity/location，同时增加随访，无法干净解释增量价值；I07 Q2b只有首次ED一维分组，未比较表示。
- reference_consensus: 9/10明确预测特征筛选或降维；8/10明确Q3b保留baseline并加随访；4/10有输入变体/筛选方案的显式比较（P01 p19、P06 p51、P07 pp47–58、P09 pp59–62）。严格验证收益未获证明。轨迹形状聚类仅2/10，不以其为多数共识。
- why_generalizable: 同时适用于静态多信息源、高维小样本、设备/用户重复测量、城市/公司面板及实验轨迹；要解决的是如何表达可用信息以及判断新增信息是否有用，不依赖HM/ED/医学实体。
- why_current_skill_is_insufficient: 已有“构造变量”“同协议比较”和fold隔离的宽泛原则；只读设计workflow及模型族未见可执行的特征组保留/增量/删组对照过程。Q3b信息丢失和Q1/Q2b缺比较表明仅靠模型族比较尚不足。不是说Skill没有任何feature engineering能力。
- expected_competition_impact: 避免合法信息无故丢失，让特征构造形成可说明、可否决的证据；有望改善预测、亚组解释和创新论证。**没有可比实验，不能承诺分数提升或给提升百分比。**
- recommended_next_phase: 经人工判断后，只验证这个特征集设计与消融候选：固定合法样本、时点、fold与受控模型，比较baseline、baseline+少量有依据表示及必要删组；保留负结果。不得把本次参考成绩回填历史run。

## G1七条件核对

| Condition | Evidence / boundary |
| --- | --- |
| 1 当前确有不足 | 完整基线在Q3b缺失；Q1/Q3未保存输入组对照；Q2b仅单表示 |
| 2 多reference明确支持 | P01/P06/P07/P09四篇比较思想，加8篇baseline保留；不是单篇偏好 |
| 3 显著影响竞赛质量 | 信息是否丢失、随访贡献能否归因、分群能否解释是核心建模问题；量化收益尚待未来验证 |
| 4 不依赖医学 | feature groups、时间摘要与表示对照适用于任何实体/量测 |
| 5 可迁移 | 静态表格、多视图、稀疏纵向/面板等多个数据结构 |
| 6 可形成清晰原则 | 保留基线，少量问题驱动表示，隔离选择，同协议增量/删组，允许无收益 |
| 7 非单篇偏好 | 9/10选择、8/10增量信息、4/10显式比较；不指定grey/DTW/PCA/XGB |

判断置信度：来源/事实HIGH，通用缺口诊断MEDIUM–HIGH；实际预测收益UNKNOWN。本轮多篇证据独立支持这一结论，即使与上一轮候选同名，也不是继承旧结论。旧报告完整保留，新增参考没有进入历史模型。

## G2 — Problem-Specific Improvement

| Item | Why not a generic Skill requirement |
| --- | --- |
| 特定脑区合并、临床分箱、区域比例×体积 | 通用的量纲/表示原则有价值；具体医学组合需领域支持 |
| HM–ED的具体滞后、病理峰值和治疗时序 | 时间间隔、采样和临床机制决定；参考没有一致可验证lag模型 |
| 48h窗口无随访者的标签/删失策略 | 当前确有4例限制；本轮记录，不从不同论文标签倒推标准答案 |

## G3 — Reference Difference Only / evidence insufficient for new G1

| Item | Decision |
| --- | --- |
| Logistic vs RF/XGB/CNN | 名称不决定优劣；P08本就选Logistic；外部成绩不可比 |
| 等实体WLS+聚类区间 vs mixed/GEE | 正确估计单位和estimand比模型名重要；不要求为了模仿改模型 |
| Gaussian/spline/LOESS vs二次曲线 | 当前选型证据不足，但已有模型比较原则；本轮不另建曲线模型目录 |
| 完整trajectory clustering专门模块 | 仅P06/P10明确；可作为唯一G1的表示候选，未证明需要独立模块 |
| 深度多模态融合/序列网络 | baseline保留是强证据；深度架构收益未证实，不要求升级 |
| Robustness/sensitivity / uncertainty | 此题实际证据不足，既有workflow存在；reference未建立明确共同优势，不抢占Top-1 |
| Q3c无独立结果、论文未完成 | 属当前run交付缺项；不能自动证明通用解释/写作能力全无，记录但不另立模块 |

## G4 — Reference Weakness

训练评价、split前重采样、观测单位混淆、无cutoff、残差/指标矛盾、importance当效应、混合模型名与结果对象不一致，详见 [reference-weaknesses.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/reference-weaknesses.md)。这些不应进入Skill。

## 推荐边界

下一阶段最多一个候选；不同时开发轨迹聚类、复杂融合、因果推断和robustness系统。此阶段 **STOP**：无Skill、routing、runtime script、历史结果修改；等待人工决定是否值得修复。
