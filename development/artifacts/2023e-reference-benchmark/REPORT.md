# 2023E Excellent-Solution Post-hoc Benchmark

结论：**GENERALIZABLE_GAP_FOUND**。Top-1为 **VALIDATION_SAFE_FEATURE_SET_DESIGN_AND_ABLATION（有验证依据的特征集设计与增量消融）**。当前方案具备较严格的行为正确性防护，但输入表示的系统比较和竞赛建模交付深度仍不足。本轮没有修改Skill、训练模型或更换历史结果。

## 1. Reference Sources

按用户指定 [GitHub E题目录](https://github.com/zhanwen/MathModel/tree/master/国赛论文/2023年优秀论文/E) 枚举全部10份PDF，固定commit为 `cd5be91735ebf11d5ee52eb170e86a6d07131977`；下载文件逐一核对Git blob SHA1、字节数和SHA256。共821页完整文件，10篇均审读九小问的相关正文方法、结果、验证和局限。

| ID | Filename | Institution | Pages | 官方奖项 |
| --- | --- | --- | --- | --- |
| P01 | E23100650012.pdf | 天津师范大学 | 59 | 一等奖，数模之星提名 |
| P02 | E23102550019.pdf | 东华大学 | 68 | 一等奖 |
| P03 | E23103530067.pdf | 浙江工商大学 | 85 | 一等奖 |
| P04 | E23103570015.pdf | 安徽大学 | 138 | 一等奖 |
| P05 | E23104030073.pdf | 南昌大学 | 60 | 一等奖 |
| P06 | E23105330424.pdf | 中南大学 | 115 | 一等奖 |
| P07 | E23106730076.pdf | 云南大学 | 109 | 一等奖 |
| P08 | E23106980022.pdf | 西安交通大学 | 53 | 一等奖，数模之星季军 |
| P09 | E23107030070.pdf | 西安建筑科技大学 | 73 | 一等奖 |
| P10 | E23900310014.pdf | 清华大学/深圳国际研究生院 | 61 | 一等奖 |

标题、作者、全部来源字段、官方名单行号、原始URL及文件校验见 [source-ledger.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/source-ledger.md)。九十个分问的逐篇记录见 [source-notes.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/source-notes.md)。页码均指含封面的物理PDF页码。

## 2. Source Reliability

**reference_quality: HIGH**；**FULL_TEXT_COVERAGE: 10/10**；**award_levels_verified: 10**。团队编号、学校、作者与 [官方最终获奖名单](https://cpipc.acge.org.cn/sysFile/downFile.do?fileId=8e7956d9a59d455ebd3866f46b155c60) 的E题sheet匹配。GitHub目录是参考集合，奖项结论来自官方附件，二者独立。

HIGH表示全文和身份可追踪，不是所有统计结果可靠，也不保证转载文件与正式提交稿逐字一致。完整审读覆盖相关正文；通用算法推导/背景略读，长附录择项静态审查，没有运行下载代码或声称逐行验证821页。关键公式和代码截图经Poppler可视核查。

上一轮较弱reference set及其报告原样保存在prior-pass-6e5d1b6；旧版“未获得可核验获奖全文”的状态已被本轮新证据更新，不沿用旧限制或自动继承旧结论。

## 3. Current Skill Solution

[当前方案摘要](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/current-skill-solution.md) 在深入读取本轮主集合前，于2026-09-15 01:01:57 UTC冻结，SHA256为 `14b72d5801fdf3afd976bf0040eeb12ff2f0e31266c0733b8f0b1bb098c57aa4`。仅使用I01–I14现有产物。上轮外部参考阅读已经披露，本轮不是新的盲跑。

原2023E run仍为 **BLIND RUN / DIAGNOSTIC ONLY**；后续Temporal、Imbalance、Ordinal、Group、Association定向升级单独列明。原run没有完整投稿论文、答案表或独立Q3c因素排序，不能把通用规则已具备写成这些交付已经完成。

当前概要：Q1时间规则+小样本分类；Q2二次曲线、baseline ED三分位、等实体权关联回归；Q3首次多视图与随访摘要，新增ordinal候选及时间边界。I09/I10升级数值仅stdout输出，本轮未找到持久副本；不补造、不重训来补数。

## 4. Q1 Comparison

Q1a基本正确性达到合理水平：onset偏移、首次HM基准、6mL/33% OR、≤48h和首次观测命中均可追踪，23/100阳性，593/593流水号时间映射。4例窗口内无随访仍记0是限制；首次观察命中也不是精确生物学发生时点。P05取最大值时点、P08公式逻辑不一致、P10相邻差公式，不应反过来替换当前规则。

Q1b当前已经使用临床、体积/部位、形状和灰度特征，并非只有原始临床字段。既有logistic盲跑AUC0.575381、Recall0.217391，RF AUC0.467532，显示保守基线尚不强；这些不是升级重复CV成绩。参考中P06 AUC0.7031也不完美，P08最终选择Logistic，说明不能把“Logistic较弱”当算法定论。

低分原因判断 **E：多种因素共同作用**。n=100、阳性23和高维冗余是数据难度；特征表示/筛选比较不足有直接证据；参考验证较弱或泄漏又使分数更乐观。没有同数据同协议实验，不能量化A/B/C/D各自贡献，也不能断言换boosting就改善。可学P01/P07/P09的输入比较思想，不复制其验证缺陷。

## 5. Q2 Comparison

Q2a当前固定二次Ridge的合法grouped RMSE为26.229155mL、MAE19.801187mL、R²−0.012561；最终fit residual RMSE25.965972mL。独立实体误差与训练残差分开是优势，固定曲线却没有足够选型证据。8篇有明确曲线族/阶数比较，P09还讨论非负和不合理远期峰；这些提示应评估形态与候选，不能据其fit RMSE6.90直接判当前更差。

Q2b是明确薄弱点：首次ED三分位34/33/33是合理baseline，fold内边界和baseline赋组安全，但相同起点不同走势无法区分。只有P06与P10明确构造实体时间形状；三篇静态、两篇观测单位有问题、三篇表示不充分。结论是“表示充分性未验证”，不是“优秀论文普遍要求DTW”。

Q2c当前crude/adjusted、time×treatment、CR1实体区间、暴露时序UNKNOWN与稀有治疗标记，较多参考更审慎。P09认识重复测量且称mixed effects，但实际表比较不同量纲变量均值差，不能证明其实现优于当前WLS。P03/P04等也有因果局限意识，应逐条评价而非一概否定参考。

Q2d当前同次HM变化每10mL的adjusted ED关联3.639mL，nominal CI[1.604,5.675]；这是限定设定中的条件关联。P01案例图提示滞后，其他多是均值/变化相关，没有共同的可靠lag/joint模型证据。当前不能称方向性动态关系或稳定治疗效果已被识别；本轮不增加复杂动态或因果框架。

## 6. Q3 Comparison

Q3a的ordinal概率候选、MAE/RMSE/QWK/Within-One和稀少等级可行性是 **SKILL STRENGTH**，但升级后效果没有持久分数证明。参考也并非全无等级意识：P06有邻近命中，P05回归取整，P07在Q3c使用累积有序Logit；该模型的汇总加权有问题，也不能等同Q3a预测。

Q3b最直接差距是：当前clinical+HM/ED摘要没有保留Q3a完整首次shape/intensity/location。8/10参考明确在基线上增加随访，P09明确21+105→126→28，P06用小样本低维摘要并前后比较。当前已有slope，不是完全不懂轨迹；但信息丢失和输入同时变更使随访收益无法干净归因。

Temporal Gate继续是硬标准。当前先过滤>2160h，原9行/8人泄漏仍失效；各参考Q3b未建立可核验cutoff，统一标REFERENCE LEAKAGE RISK，不宣称每篇实际都使用了90天后记录。当前90day上界本身仍不等于统一早期landmark预测。

Q3c参考有因素图/检验/重要性和解释，当前缺独立mRS排序产物。此处是实际交付缺项；不能用Q2的ED关联替代，也不因参考建议详尽就接受importance→causal risk factor。

## 7. Reference Consensus

[完整统计定义与排除规则](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/reference-consensus.md)：

- 9/10有明确预测特征筛选/降维。
- 8/10明确Q3b保留baseline再加followup。
- 4/10有输入变体/筛选方案的显式比较：P01、P06、P07、P09。
- 8/10有明确Q2a曲线族或阶数候选比较。
- 2/10明确实体时间形状分组：P06、P10。
- 3/10明确Q3b时间导向摘要：P01、P05、P06。
- 0/10证实完整的新实体Q2 grouped CV及Q3b逐条目标前cutoff。

出现次数不证明正确性；最后两个0表示审读未建立证据，不是复现证明全部泄漏。

## 8. Validation Comparison

**SKILL ADVANTAGE**：fold内预处理、实体零重叠、时间可得性、失效证据保留、残差与预测误差分开、适当的不平衡/序数指标。

当前Q2 row-random RMSE26.344805，反而略高于grouped26.229155；仍因实体重叠被INVALIDATED。不得为了展示泄漏乐观而改变这个事实。重复CV协议、Brier等存在，也不能声称校准曲线、bootstrap或完整稳健性结果已经产生。

外部分数全部 **NOT DIRECTLY COMPARABLE**。P01训练评分、P07 split前SMOTE、P09标签来源与正文/附录不符、P10跨模型不同切分，均限制结论。详见 [validation-comparison.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/validation-comparison.md)。

## 9. Feature Engineering Comparison

当前已具备字段整合、radiomics、变化/slope和非线性时间项。真正缺少的是：围绕输入信息源和时间窗口组织少量表示假设，保留原baseline，固定样本和合法协议，验证特征组增量/删组而非只比较模型名。

P01的表示消融、P06的基线+随访摘要、P07两套筛选交叉比较、P09保留基线的前后比较独立支持这个思想。它们的分数不被采纳为无泄漏收益证据。详见 [feature-engineering-comparison.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/feature-engineering-comparison.md)。

## 10. Trajectory Modeling Comparison

P06不等长序列标准化→插值→DTW距离矩阵→普通KMeans，是距离轮廓表示，不能叫直接优化DTW中心；P10用初/中/末斜率构造三维表示。两者都比单baseline包含更多形状，但未来轨迹参与回顾性分组不等于可在baseline预测新实体。

Q3b可借鉴低维时间摘要候选，不机械添加peak/AUC/curvature、functional clustering或大RNN。某个表示是否有信息，要在合法观察窗口下比较。详见 [trajectory-comparison.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/trajectory-comparison.md)。

## 11. Modeling Depth Comparison

当前强项是估计目标与数据边界纪律；薄弱点是候选表示、曲线选型证据、亚组画像、输入增量归因以及Q3c结果完整性。

创新A类（可迁移）包括问题驱动表示、保留基线做增量、验证隔离的对照；B类是具体脑区/病理指标；C类是没有同协议收益的算法组合。下一阶段只考虑A类中的一个明确缺口。当前已有baseline/模型比较/变量创新原则，不能把所有执行不足都包装成新模块需求。

## 12. Paper Quality Comparison

参考具有完整摘要、假设、符号、流程图、模型、结果和讨论；P06/P10的趋势画像、P01消融和P09域内特征解释提升了建模可读性。部分长篇通用推导、失真指标和过强医学建议并不值得学。

当前没有完整投稿稿，不能给不存在的摘要或结果图高评价；其代码、契约和失效历史的可追溯性较强。Q3c与论文完成度差距先归为实际run交付不足，不直接证明write-paper缺新规则。[paper-quality-comparison.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/paper-quality-comparison.md)逐项记录，workflow未改。

## 13. Skill Strengths

明确独立单位与预测边界；不把450条记录当450个独立样本；不平衡/ordinal指标与baseline；fold内学习；Group+Temporal独立gate；残差与OOF区分；未知治疗时间、稀有组与confounding纪律。行为正确性优势应保留，不以模仿参考换高分。

## 14. Skill Weaknesses

已有预测证据尚不强，升级数值部分未留档；Q2固定二次式与静态亚组的充分性未比较；Q3b没有沿用完整基线输入；Q3c无独立结果；没有完整竞赛论文或验证全面的模型解释。不用测试全PASS或方法规范来掩盖这些建模和交付限制。

## 15. Reference Weaknesses

确认实例：P07 p78先SMOTE再split；P08 p20更换正类计数且F1矛盾；P08 p27残差比值；P04 p97 MAE/RMSE/MSE不一致；P10 pp22–23绝对残差为负；P09 p41混合模型名下比较不同量纲均值；P01/P09附录训练评分。

另有全随访cutoff风险、过强因果建议、观测/实体混淆、测试标签来源或预处理隔离不清。确认缺陷与未验证风险分开，详见 [reference-weaknesses.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/reference-weaknesses.md)。

## 16. Generalizable Gaps

仅一个G1：**VALIDATION_SAFE_FEATURE_SET_DESIGN_AND_ABLATION**。事实链为当前Q3b丢完整基线、Q1/Q3输入组比较缺失、Q2b单一表示，加多篇参考的结构化输入/增量比较思想。

只读检查当前设计workflow、模型族和innovation参考：已有宽泛变量构造与同协议原则，尚未形成特征组保留/增量/删组对照的具体流程。诊断是操作能力不足，不是“完全不懂特征工程”。[generalizable-gaps.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/generalizable-gaps.md)逐项核对七个G1条件和G1–G4分类。

## 17. Problem-Specific Differences

脑区合并、临床分箱、具体HM–ED滞后与病理峰值属于G2。Logistic/boosting、WLS/mixed、Gaussian/spline不同本身属于G3。参考泄漏和因果/指标问题属G4。

完整trajectory-clustering模块没有多数共识；深度融合/大型序列模型收益未验证；robustness/sensitivity本轮不解决也不另列Top-1。Q3c及论文未完成属于已存在交付要求的执行差距，不自动扩展Skill。

## 18. Top-1 Recommended Skill Improvement

- gap_name: VALIDATION_SAFE_FEATURE_SET_DESIGN_AND_ABLATION
- evidence: I01/I09/I10的输入集不连续与未保存组比较；I07的单表示分组。
- reference_consensus: 9/10选择/降维，8/10保留baseline，4/10显式输入比较；具体页码见第7节。
- why_generalizable: 静态高维、多源融合、设备/用户重复记录、城市/公司面板均需要表达与增量价值判断。
- why_current_skill_is_insufficient: 模型族对比及泄漏gate不能自动防止合法信息丢失，也不能说明某表示为何有用。
- expected_competition_impact: 减少信息丢失，改善可解释的建模论证和收益归因；预测提升幅度UNKNOWN，不能承诺。
- recommended_next_phase: 人工确认后，仅验证特征集设计与合法增量消融；在固定时点、样本、fold和受控模型上比较baseline与少量表示，允许负结果，不回填历史run。

## 19. Current Skill Level on 2023E

| Scope | Level | Evidence |
| --- | --- | --- |
| Q1 | ADEQUATE | 标签/时间规则可追溯，多视图及不平衡验证合理；预测表现与特征组收益不足，4例观测窗口限制 |
| Q2 | WEAK | Q2c/d关联纪律较强，但整体曲线R²接近0且未选型、Q2b静态表示未证明充分，核心轨迹建模深度不足 |
| Q3 | WEAK | ordinal/time纪律较强，但Q3b丢基线，升级分数未留档，Q3c独立因素结果缺失 |
| Overall | NEEDS_MODELING_IMPROVEMENT | 安全可靠的流程基础已经存在，输入表示和竞赛交付的质量证据仍不足 |

这些等级不是以参考训练accuracy打分，不表示获奖论文逐项都更好。

## 20. Final Decision

**GENERALIZABLE_GAP_FOUND**

**2023E_REFERENCE_BENCHMARK_COMPLETE**

- reference_quality: HIGH
- papers_discovered: 10
- papers_fully_reviewed: 10（相关正文九小问完整审读；长附录择项审查）
- award_levels_verified: 10
- overall_skill_level: NEEDS_MODELING_IMPROVEMENT
- top_generalizable_gap: VALIDATION_SAFE_FEATURE_SET_DESIGN_AND_ABLATION
- recommended_next_action: 等待人工判断是否开展“特征集设计与合法增量消融”这一单一候选修复。

[completion.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/completion.json)和[integrity-verification.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/integrity-verification.json)记录最终状态与文件边界核查。本轮未重跑训练/回归；此前226 pytest和20 harness通过只作历史行为证据。Skill、routing、历史benchmark、冻结模型与失败证据按哈希保护；报告仅写本artifact目录，gitignore不变。

**STOP。等待人工判断，不自动修改Skill或进入下一开发阶段。**
