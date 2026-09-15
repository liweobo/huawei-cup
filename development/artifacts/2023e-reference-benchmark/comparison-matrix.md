# Question-by-Question Comparison

当前侧事实来自阅读参考前冻结的 [current-skill-solution.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/current-skill-solution.md)，I01–I14是其中的内部证据。参考身份见 [source-ledger.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/source-ledger.md)，原文定位见 [source-notes.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/source-notes.md)。比较的是问题解决能力与证据，不按算法名称或奖级排名。G1–G4的定义与唯一候选见 [generalizable-gaps.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/generalizable-gaps.md)。

| Question | Skill Approach | Reference Approach | Skill Strength | Skill Weakness | Generalizable Gap? |
| --- | --- | --- | --- | --- | --- |
| Q1a | 流水号恢复时间，发病偏移，≤48h且≥6mL OR ≥33%，取首次观测命中；23/100阳性 [I01–I05] | B07按同一阈值/偏移；B03拟合曲线求阈值根；B08手动把48.90h改48h；B02仅首次随访/33% | 确定性规则、593/593时间映射、保留观测过程；没有凭曲线外推制造观测标签 | 4人48h内无随访仍编码0，应区分未观察到和确认阴性；首次命中非精确生物学起点 | G2：本题标签审计待补；已有缺失/时序规则，不由此新建模块。B08/B02为G4。拟合事件时间是G3，不自动更好 |
| Q1b | 临床+首次HM/ED体积/位置+形状/灰度；正则化/类别权重Logistic与浅RF；当前重复分层CV、PR-AUC优先 [I01/I03/I09] | B03六模型+SMOTE；B07 RF/LightGBM集成；B08 73→7特征再比较RF/NN/SVM；B04 72维ISSA-BP | 已使用影像多视图，非只喂临床字段；防重采样泄漏、多数类对照、概率指标；不过度容量 | 冻结AUC0.575381、少数类recall0.217391说明原方案弱；没有持久化的特征组消融/去冗余比较；升级分数未保存 | G1候选的主要证据：有控制的特征组设计与消融缺少实际验证。模型名字差异为G3；不能断言换Boosting必优 |
| Q2a | time-only二次Ridge；100人450行；5-fold grouped；最终残差与新实体误差分开 [I06/I07] | B01二/三次/高斯比较，B04双高斯；B07混合效应+BiLSTM并使用首次ED；B08三次多项式 | 合法实体独立评价，overlap=0；明确允许选定方法后全体最终拟合 | 只固定一种曲线；grouped RMSE26.229155mL、R²−0.012561，尚未证实能解释进展；缺曲线参数的实质解释 | 曲线族比较是值得保留的建模观察；尚无可比证据证明某种复杂曲线优越，不另立Top-1。不能将time-only均值曲线和带个体baseline模型同榜 |
| Q2b | 首次ED三分位、三组二次曲线；训练实体内定边界，验证者按baseline赋组 [I06/I07] | B01静态临床K-means四组；B04静态FCM五组；B08混合类型两步聚类四组；B03声称各次ED等但时间表征不清；B07重要性选10变量后K-means | 合理、透明baseline，分组可在预测时实施；fold内discovery有实证 | 一维幅度不直接刻画形态；未比较多维/动态表征、簇画像或同协议收益，不能称成熟进展亚组发现 | G1候选的旁证是表征选择未经比较。没有“优秀方案普遍完整轨迹聚类”的证据；DTW/functional clustering不列为必修 |
| Q2c | 7措施prevalence/共现/初始差异，crude/adjusted，equal-entity WLS+cluster CI，time×exposure；时点UNKNOWN [I08] | B01/B04 ANOVA；B03 GLM/28组合；B07 t检验；B08末次−首次变号后分类判“有效” | confounding-by-indication、处理前调整、实体依赖、小样本与因果措辞纪律明显较严 | 急性处理前严重程度和共同治疗未充分控制；名义区间探索性，不能给因果结论 | 不缺默认propensity/causal ML；对应参考的越界措辞为G4。未见必须新增通用因果能力的证据 |
| Q2d | 时间、HM初始/同次变化、少量治疗、合理baseline的联合条件回归；100人350随访 [I08] | B01拟合参数Spearman；B04 HM/ED相关；B07 ACF/PACF和分组t检验；B08卡方/决策树 | 比简单成对相关更明确地控制时间和基线；清楚说明HM不是已核验的治疗前confounder | 同次HM与ED变化不能识别滞后方向；没有跨设定稳定性证明 | G2：特定HM–ED动态假设可后续研究；本组参考没有可信lag收益支持新的通用动态模块 |
| Q3a | 首次多模态；nominal与cumulative ordinal候选、4×2重复CV；MAE/RMSE/QWK/Within-One-Level [I03/I10] | B03 BP/ACO；B07 DeepForest及top10；B08承认顺序、尝试回归后选RF并筛12指标 | 正式ordinal建模与距离指标是SKILL ADVANTAGE；n=100容量受控 | 原nominal MAE1.53、QWK0.230461；升级ordinal数值未持久化，不能宣称提高；缺特征组比较 | G1候选主要证据之一。G3：没有NN/DeepForest不构成缺陷；参考有一定序数意识但不是正式ordinal验证 |
| Q3b | 90天过滤后每实体first/last/max/change/slope；clinical+体积聚合；一实体一行；原超时9行/8人结果失效 [I01/I03/I10/I11] | B03保留静态视图并融合时序分支；B07时间间隔+序列+PCA/LSTM；B08前两次随访影像 | Temporal Gate与entity split；不会复活失效成绩；模型简单可查 | 未保留Q3a完整首次形状/灰度/位置，因此“随访增益”与特征删减混杂；90天截止也不是统一早期预测landmark | G1候选最直接实例：需保持共同特征基线再做同cutoff增量消融。参考无截止证据为REFERENCE LEAKAGE RISK；B07全量PCA为已确认G4 |
| Q3c | 有因果措辞边界；未见独立mRS因素排名/系数/SHAP等持久产物 [I01/I12–I14] | B03相关检验；B07Pearson/importance表；B08相关筛选+岭系数+临床解释 | 不把预测importance写成因果因素，不将Q2的ED关联偷换成mRS分析 | 现有产物确实不完整，无法评价解释的稳定性或清晰度 | G2：补齐本题解释交付；此轮不足以证明需要新解释算法模块。参考的因素输出形式可学，因果外推为G4 |

## Q1b：较低分数的四种解释

| 解释 | 本轮证据判断 |
| --- | --- |
| A 数据本身难 | n=100、23阳性、高维、异质性、部分影像join缺失支持小样本困难；不能由此证明当前方法已最优 |
| B 特征工程不足 | 有直接证据：没有同协议特征组/缩减比较；不是没有radiomics。B07/B08的显式特征比较提醒应验证表示与维度，而不是照抄其筛选结果 |
| C 模型选择不足 | 原方案候选有限，但已经有Logistic与浅RF。没有同特征、同split、无泄漏的模型对照，无法证明某个模型族被错过就是低分主因 |
| D 更严格验证导致保守 | B03全量SMOTE和B07训练/内部重复样本评价足以使高分不可比；这能解释部分“分数差距”，不能量化贡献，也不能把全部弱结果归因于验证严格 |

本轮结论：**B是可操作且跨题的诊断；A/D有支持但无法分摊贡献；C未证实。** 因而只推荐特征组设计与消融能力，不推荐按排行榜替换模型。
