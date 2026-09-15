# 2023E Excellent-Solution Post-hoc Benchmark

日期：2026-09-15（北京时间）。当前仓库提交：cce0a80d03aef5ec69713cac5afa85cb154933b7。

**Final Decision: GENERALIZABLE_GAP_FOUND**  
**reference_quality: MEDIUM**  
**Top-1: VALIDATION_SAFE_FEATURE_SET_DESIGN_AND_ABLATION**

当前Skill的泄漏防护、序数建模和观察性关联纪律已有明确优势；已保存方案在特征组设计、信息增量比较与完整建模交付方面仍不足。本轮没有证据支持按模型名称替换方法，也没有证据支持“获奖方案普遍采用完整轨迹聚类”。

## 1. Reference Sources

[Source Ledger](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/source-ledger.md)记录每个来源的作者、URL、奖项核验、发表状态、全文范围与置信度；[Source Notes](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/source-notes.md)提供具体页码/源码行号。

- R-A01：竞赛官网最终获奖名单；R-A04：西安交大官方获奖新闻。
- R-B01/R-B04：两篇正式发表的曲线、静态亚组及治疗关联研究；与同题结构高度一致，数据版本未完全核实。
- R-B02：正式发表的Q1/Q2文章，主要作为方法缺陷对照。
- R-B03/R-B07：作者公开完整参赛稿、LaTeX及可静态审查的代码。
- R-B08：作者公开原参赛PDF；与作者后来复盘改进的代码分开。
- R-B05：部分MATLAB实现，仅辅助；R-B06主要题面转录，排除出核心比较。
- R-C01：南昌大学论文封面，与官方一等奖记录匹配，正文不可获得。

## 2. Source Reliability

**NO VERIFIED FULL AWARD PAPER AVAILABLE**：本次未获得能核验为一/二/三等奖的完整论文。南昌大学队号23104030073及三名队员与官方E题名单第10行匹配，奖项为一等奖，但文档站只提供可读封面；不能推断其方案。R-B03文字层队号23118450049在官方表第5043行是成功参与奖，不能包装成优秀奖项。R-B05/R-B08自述三等奖未能独立核验；R-B07奖级UNKNOWN。官方优秀作品WPS集合需要登录。

因此本轮采用官方信息、正式发表研究、作者公开方案组成REFERENCE SET，可信度MEDIUM。来源真实性、奖项真实性、方法有效性是三件事。没有把第三方标题或GitHub星数当奖项证明，也没有把获奖当ground truth。

## 3. Current Skill Solution

[冻结摘要](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/current-skill-solution.md)在首次外部检索前形成，SHA256由[current-solution-freeze.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/current-solution-freeze.json)记录。以下事实均来自既有产物。

| 子问 | 已保存方案与结果 | 主要限制 |
| --- | --- | --- |
| Q1a | 时间恢复+48h、6mL/33%规则；23阳性/77阴性 | 4人48h内没有随访却编码0；不是确定无事件 |
| Q1b | 首次临床/影像多视图，Logistic/浅RF；原Logistic AUC0.575381 | 当前升级重复CV数值没有持久副本；无特征组消融 |
| Q2a | 二次Ridge；100人450行；grouped RMSE26.229155mL，R²−0.012561 | 固定单一曲线，尚未解释足够个体/时间差异 |
| Q2b | 首次ED三分位，34/33/33；fold内边界和曲线 | 是baseline，未验证多维/形态表示价值 |
| Q2c | 7措施crude/adjusted WLS、实体聚类CI、time interaction | 治疗时间未知，部分稀有比较不稳定，非因果 |
| Q2d | HM/ED变化、时间、少量治疗和基线的联合条件关联 | 没有lag/因果方向或跨设定稳定性证明 |
| Q3a | 原nominal MAE1.53、QWK0.230461；当前有ordinal候选/重复CV | 升级ordinal数值未持久化，不能声称更准 |
| Q3b | 90天过滤后体积first/last/max/change/slope；原corrected MAE1.42、QWK0.342714 | 未保留Q3a完整首次影像视图；非固定早期landmark |
| Q3c | 有claim语言约束 | 未找到独立mRS因素分析的持久输出 |

重要范围限制：原run明确为BLIND RUN / DIAGNOSTIC ONLY，后续是定向能力升级；未找到完整比赛论文、最终答案表或完整主模型选择产物。本轮不将这些局部证据反向美化为已完成的优秀论文。

## 4. Q1 Comparison

Q1a的主体规则达到合理水平：当前用发病偏移恢复小时数，6mL对应原始单位6000，两个扩张阈值为OR，取≤48h内首次观测命中，593个影像流水号时间映射均覆盖。R-B07实现也使用相同核心规则。R-B08注意到流水号不一致和4个晚随访病例，但把48.90h手动改为48.00h；R-B02遗漏6mL条件并混淆首次检查与发病。参考并不是标签答案。

当前仍需说明4名无48h内随访者的可观测性，且“第一次检查发现”不同于扩张精确起点。这里只记录，不改原标签。

Q1b不能按accuracy比较。当前已纳入首次体积、位置比例、形状/灰度和临床字段；短板并非完全没用影像特征。原预测成绩较弱，原因判断是：小样本/类别不平衡有支持；**有证据的可改进方向是特征组及维度比较不足**；遗漏某模型族尚无可比证据；参考全量SMOTE、训练评价等会造成更乐观数字，但无法分摊全部分数差距。详见[逐题矩阵](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/comparison-matrix.md)。

## 5. Q2 Comparison

Q2a：R-B01比较二次/三次/高斯，R-B04用双高斯，R-B08比较多种曲线；R-B07提出ID混合效应和序列方法。当前仅固定二次Ridge，缺少针对曲线形状、峰值/回落与个体差异的充分论证。负的pooled grouped R²说明目前未展现有用的新实体预测能力；它不单独证明换曲线必有收益，time-only总体均值本就不能解释全部个体差异。R-B07加入首次ED后已是不同条件模型，也不能与time-only曲线共榜。

FIT_RESIDUAL与VALIDATION_ERROR必须区分：既有最终全体拟合残差RMSE25.965972mL，合法grouped OOF RMSE26.229155mL；row-random为26.344805mL且共享实体，INVALIDATED。本次row分数没有更好，不能捏造泄漏乐观程度。选定方法后在全部训练实体上最终拟合是正常流程。

Q2b：首次ED三分位是合理、可部署的baseline，但不足以证明已发现进展异质性。多数参考实际按静态临床特征聚类；B07增加重要性选择与部分变化信息，B03声称各次体积但未清楚处理对齐。参考没有建立“完整trajectory shape聚类普遍更优”的证据。本轮发现的是**表征选择与合法分组收益比较缺失**，不是必须增加DTW或特定聚类算法。

Q2c：当前先审计prevalence/共现/初始差异，明确暴露时点UNKNOWN，比较同样本crude/adjusted并按实体处理依赖。它比多篇参考直接ANOVA/t检验/末次变化→疗效的解释更严格，是SKILL ADVANTAGE。仍不能排除急性严重程度及共同治疗混杂。

Q2d：当前HM变化每10mL对应ED变化的adjusted条件关联为3.639mL，名义95%CI[1.604,5.675]；这是同次测量关联，不是因果或lag作用。参考多为成对相关/曲线参数关系；B07提ACF/PACF，但没有可信的不规则访视lag识别证明。本轮不足以推荐复杂动态模型。

## 6. Q3 Comparison

Q3a：当前正式ordinal候选和MAE/RMSE/QWK/Within-One-Level更贴近mRS性质。B03/B08并非完全没有顺序意识，但主要用nominal分类或回归后取整；不能仅因模型不同扣分。当前升级后数值缺持久副本，所以只能确认能力和协议，不能宣称ordinal已经提高成绩。

Q3b：当前Temporal Gate排除了>90天记录，原9行/8人的失效证据保留；聚合后一实体一行的row CV等价于entity CV。参考B03/B07/B08未给可核验cutoff；前5次或前2次并不是90天过滤。统一标REFERENCE LEAKAGE RISK，确切>90天使用仍UNVERIFIED；不套用当前方案的9条记录数量。

更直接的当前缺项是Q3b没有延续Q3a完整首次shape/intensity/location矩阵，导致“加随访”的效果与“删首次视图”混杂。B03明确保留静态分支后融合随访，B07/B08也注重多视图/特征筛选。可学的是保持信息基线并做受控比较，无需照搬LSTM。

Q3c：参考有相关图、重要性表或岭回归系数；当前未找到mRS专属因素输出，构成交付弱项。当前因果措辞纪律值得保留，但不能替代实际因素分析；Q2的ED关联不等于Q3c答案。

## 7. Validation Comparison

[详细协议对照](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/validation-comparison.md)。

当前的真实实体零重叠、fold内预处理/亚组边界、90天前过滤、失效结果保留、类别与序数指标，是明确SKILL ADVANTAGE。B03公开源码确认全量SMOTE/缩放先于CV；B07 Q3b确认全量PCA后才split；部分Q2分组收益只来自训练拟合。这些分数不能作为优秀性能标准。

优势不覆盖一切：当前未保存升级后全部数值，没有外部验证或可靠性曲线，fold标准差不是置信区间，association名义CI不是稳健/因果证明。描述性聚类可以对完整训练数据拟合；只有把它当新实体/未来验证时才必须额外满足对应gate。所有外部数值对比结论均为NOT DIRECTLY COMPARABLE。

## 8. Feature Engineering Comparison

[详细特征对照](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/feature-engineering-comparison.md)。

当前已经有多表join、血压拆分、影像比例/形状/灰度、体积变化和斜率，并非“只喂原始字段”。实际遗漏是：缺少少量任务驱动的特征集合、冗余/容量比较、保持共同基线的新增信息消融。B08针对n=100、p=73明确做缩减；B07比较all vs top10；B03保留静态+时序视图。这些独立方案支持应验证信息表示，不支持照抄特征名单或筛选阈值。

## 9. Modeling Depth Comparison

当前方案的安全边界深于多数已读参考，但部分模型停在baseline，尚未形成完整的“为什么这样表示数据—选择怎样的模型—新增信息带来什么收益”的论证。

创新分三类：A，可迁移的特征表示、多视图保留和验证内消融值得学习；B，特定脑区/临床严重程度组合属于本题或专业领域；C，无同协议验证收益的群智能优化、网络叠加或模型改名不能算应增加的能力。高容量模型在约100个独立实体上的风险必须与收益共同判断。

## 10. Paper Quality Comparison

[论文要素对照](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/paper-quality-comparison.md)覆盖摘要、重述、假设、符号、构建/求解、图表、评价、优缺点、创新与实际解释。

没有完整Skill论文可逐段比较，不能给不存在的摘要打分。参考的曲线参数表、特征消融表、因素解释使交付更完整；参考中的训练成绩包装、未经支持的因果假设和图表口径混乱应拒绝。本轮不修改write-paper，也不把诊断阶段没写论文认定为通用写作能力已被证伪。

## 11. Skill Strengths

- 时间、实体与预测场景相互独立地约束评价；有可追溯失败和有效结果。
- 不平衡分类不以多数类accuracy取胜；ordinal目标有匹配的模型候选和误差指标。
- 观察性措施分析保留混杂、时序和依赖限制，不把治疗组差异写成疗效。
- 低容量baseline、实际运行和数据来源可查；不编造未持久化数字。

## 12. Skill Weaknesses

- 缺少可追溯的特征组比较，Q3b共同基线缺失尤其明确。
- Q2总体曲线和分组目前只展示简单baseline，未充分解释进展异质性或证明改进。
- 原Q1/Q3预测分数弱；升级后成绩不可从持久产物确认。不能用规则成熟遮盖结果不足。
- Q1可观测性边界、Q3c独立因素输出与完整论文交付仍有本题缺项。

## 13. Reference Weaknesses

- 全量SMOTE、缩放/PCA先于split；训练或内部调参成绩冒充外部泛化。
- 缺少实体独立/明确cutoff证据；时序模型名称不能代替真实时间输入和split核验。
- 观察性相关、t检验、ANOVA或importance推导治疗有效/有害。
- 手动把48.90h改48h、遗漏阈值/时间基准、把MAE汇总称RMSE或残差单位不一致。
- 部分奖项/完整方案不可核验；B02摘要包含正文没有的Q3内容。

这些问题按原文/代码证据与风险级别分别记录，不推断作者动机，也不借参考缺陷宣布Skill整体“优秀”。

## 14. Generalizable Gaps

[完整分类与Top-1证据](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/generalizable-gaps.md)。

唯一推荐G1是VALIDATION_SAFE_FEATURE_SET_DESIGN_AND_ABLATION。具体临床变量、4个标签可观测性病例和本题未完成的因素交付归G2；模型名字、未证实的轨迹算法/lag优势归G3；参考泄漏和因果越界归G4。

当前Skill已经有“特征选择应在fold内”的行为规则。缺口是建模指导和验证实绩的深度：选择哪些有理由的特征组，如何保留共同基线，如何区分表示收益和模型容量收益。

## 15. Problem-Specific Differences

本题特殊的HM/ED含义、脑区比例、治疗前严重程度、流水号冲突和检查时点例外，不应成为通用Skill硬编码。Q3c及论文的补齐是本题交付工作。对于HM–ED滞后关系，只有合适时序与访视支持时才有研究意义，本轮没有证据把它升为通用必修。

## 16. Top-1 Recommended Skill Improvement

- **gap_name:** VALIDATION_SAFE_FEATURE_SET_DESIGN_AND_ABLATION
- **evidence:** 当前Q1/Q3缺特征组比较；Q3b删除Q3a部分首次影像视图；Q2b只比较一维baseline的合法性。
- **reference_support:** B07 all/top10比较，B08去共线性与小样本降维，B03静态+时序信息保留；均有明确原文/源码位置，均不拿其分数证明优越。
- **why_generalizable:** 小样本多变量、多来源融合、阶段信息的增量评估普遍存在于临床、机器、用户、城市、企业和实验数据。
- **why_current_skill_is_insufficient:** 已有安全gate不能替代特征设计和受控消融；本题没有证明现有表示充分利用可用信息。
- **recommended_next_phase:** 只围绕这项能力，在同一目标、实体、cutoff、fold与指标下比较少量预先说明理由的特征组和fold内筛选；不预设复杂方案获胜，不复制论文参数。

此建议是下一阶段候选，非已实施改进，也不保证将来分数提高。轨迹聚类暂不选Top-1，因为参考主要静态分组且无可靠同协议优势证据。

## 17. Current Skill Level on 2023E

| 范围 | 判断 | 具体依据 |
| --- | --- | --- |
| Q1 | ADEQUATE | 标签主体规则和首次信息/不平衡验证合理；4例可观测性和原AUC/Recall弱，未达到强预测证据 |
| Q2 | WEAK | Association纪律较强，但总体曲线和亚组建模仍为baseline；grouped R²负、没有表征/曲线的合法改进比较；不是所有Q2分析都无效 |
| Q3 | WEAK | 有ordinal/temporal优势，但升级数值缺持久证据、Q3b融合不完整、Q3c无独立输出 |
| Overall | NEEDS_MODELING_IMPROVEMENT | 行为正确性不等于完成高质量比赛建模；共同特征基线、表示比较和问题交付尚不足 |

这些判断针对已展示的方案，置信度MEDIUM；不是奖项预测，也不是对全体获奖论文的排名。

## 18. Final Decision

**B. GENERALIZABLE_GAP_FOUND**

存在一个值得进入下一阶段验证和修复的通用能力缺口：**在合法验证内设计特征组，并通过同协议消融确认增量价值**。本轮不选择“没有任何值得立即修复的通用缺陷”。

**Completion: 2023E_REFERENCE_BENCHMARK_COMPLETE**  
**reference_quality: MEDIUM**  
**top_generalizable_gap: VALIDATION_SAFE_FEATURE_SET_DESIGN_AND_ABLATION**  
**recommended_next_action:** 下一阶段仅验证并补齐特征组设计与消融比较能力，保留既有Temporal、Group、Ordinal、Imbalance与Association边界。

冻结文件及原摘要校验见[integrity-verification.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/integrity-verification.json)，机器可读完成记录见[completion.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/completion.json)。本轮只写独立artifact，保留gitignore；未重训模型、运行旧建模测试来补数、替换历史结果、修改Skill或启动下一阶段。
