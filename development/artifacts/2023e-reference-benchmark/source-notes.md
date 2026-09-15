# Reference Reading Notes and Evidence Anchors

以下是事后阅读记录，不属于原 BLIND RUN。页码一律是下载PDF的物理页码；LaTeX/源码使用本地忠实文本副本行号。CONFIRMED 指原文或源码明确展示；RISK / UNVERIFIED 指缺少足以核实实际执行的证据。未运行任何外部代码。

## R-B01 — 已发表的曲线与亚组分析

[原文PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B01.pdf)；[DOI](https://doi.org/10.12677/mos.2024.135465)。

- PDF pp.2–5：100人、发病至影像小时数、ED体积散点；比较二次、三次和一维高斯曲线，依靠拟合图选择高斯。没有独立实体留出成绩。不能把“曲线更贴近散点”当泛化提升。
- p.6：聚类输入明列年龄、性别及病史/生活史等静态变量；K-means四组。p.5的“9个不同特征类型变化趋势”不能读成九维纵向形态表示。
- pp.7–9：将拟合高斯参数用于多因素ANOVA，并比较HM/ED参数的Spearman相关。它提供“把曲线压缩成可解释参数”的思路，但未证明参数在稀疏随访下可稳定辨识。
- p.8、p.9结论将统计关联引向“更有效的方法”，没有干预时序或混杂识别证据。UNSUPPORTED_CAUSAL_CLAIM。
- 可学的是曲线形式比较、参数化解释与多维分组思路；不能采纳其因果解释，也不能确认高斯一定优于当前二次模型。

## R-B02 — 正文覆盖范围与明显方法缺陷

[原文PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B02.pdf)；[DOI](https://doi.org/10.12677/aam.2025.141027)。

- pp.3–5：正文用首次与随访1的相对变化 >33%、两次检查间隔≤48h判断；未保留6mL的OR条件。模型假设还将首次检查等同发病。与本轮Q1标签定义不等价。
- p.6：写前100预测后60，再将后60当训练集预测前100；没有真实测试标签或独立验证证明。
- pp.7–9：将时间字段截取前八位；436点做线性拟合；Q2b把合并后的y值分成五个等频箱。不能证明这是每患者唯一的进展亚组，也没有时间基准正确性证据。
- pp.11–12：由相关性的符号直接写治疗减小/增加水肿，甚至出现正相关解释成减小。UNSUPPORTED_CAUSAL_CLAIM，且方向解释有矛盾。
- 全16页正文只有Q1/Q2，摘要中的mRS、XGBoost/LightGBM没有对应Q3方法与结果。不得把摘要承诺当实际成果。
- 此文只作参考质量反例，不支撑Skill必须增加某个模型。

## R-B03 — 完整公开参赛稿与静态代码核验

[论文仓库](https://github.com/spiritysdx/CPGMCM_2023)；[可读LaTeX](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B03-tex-read-only.txt)。官方名单仅对应成功参与奖，不能称一等奖/优秀获奖论文。

- Q1a，LaTeX L178–224：六种函数按同一患者拟合R²选优，再求48h阈值根。这是拟合/插值推断事件时间，区别于首次观察到满足阈值的时间；不能当标签ground truth。
- Q1b，L333–396：80/20、网格搜索、10/15折、SMOTE、F1选择。表中MLP AUC=0.7591、F1=0.7533只是作者报告值。
- [Q1b代码L105](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B03-q12-code-read-only.txt:105)全表缩放，L113–114、L158–161先SMOTE后split；L266–281直接在已重采样矩阵上GridSearchCV/cross_val_score。CONFIRMED PREPROCESSING/RESAMPLING LEAKAGE IN PUBLIC CODE；不再把这些分数当可信对照。
- Q2a，L449–474：发病置零，高斯曲线；逐次残差observed−fitted，最终每人填残差绝对值之和。其量纲/聚合权重与Skill pooled OOF RMSE不同。
- Q2b，L538–564：声称使用年龄、性别、各次ED值，比较四种聚类、3–5簇；未明确不规则时间对齐、缺访处理或形态距离。公开[q22代码L113](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B03-q22-code-read-only.txt:113)另拼接临床/治疗列，再按列位置取输入；[搜索代码L25](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B03-q22-search-code-read-only.txt:25)重复全样本搜索并以全样本silhouette选结果。不能只凭“K-means”称其完成了可信trajectory clustering。没有新实体分组/曲线OOF检验。
- Q2c/d，L604、L650、L678、L756：7项措施与28组合，趋势为相邻增减方向计数，GLM/ANOVA。作者讨论了共线性/因果边界，但后文仍宣称某治疗效果最好；没有可靠识别支持。
- Q3a/b，L891、L1015明确先SMOTE后分训练/测试；L968–1008保留静态信息并另建带时间间隔的LSTM后融合。思路是模态保留和时间信息表示，不等于证明其高容量模型必要。
- Q3b：原文使用“所有影像结果”，没有可核验的90天或固定landmark截断。REFERENCE LEAKAGE RISK；本轮未核实其最终模型实际纳入了哪几条>90天记录，不能把Skill的9条/8人直接套给该论文。
- Q3c，摘要L35–36与L1099之后：区分有序/无序变量，统计检验和相关性；使用SMOTE后的样本作推断的独立性不成立。承认部分序数意识；未见正式ordinal预测损失或QWK验证。

## R-B04 — 神经网络和静态FCM

[原文PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B04.pdf)；[DOI](https://doi.org/10.12677/mos.2025.143212)。

- pp.4–7：72输入的ISSA-BP，训练/“测试集2”AUC称在0.85–0.95，“测试集1”为0.59。真实测试标签来源及独立验证协议不充分，不能与Skill OOF AUC排名。
- pp.7–10：总体双高斯曲线；FCM五组输入是年龄、性别、病史、治疗等静态信息，非完整trajectory shape。
- p.10给各组高斯参数，是可解释输出形式；未给grouped validation。
- pp.10–11：ANOVA被解释为治疗效果，结论和部分不显著检验不一致。不能据此降低Skill的观察性证据标准。

## R-B05 / R-B06 — 辅助或排除材料

- R-B05 [Q2a源码](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B05-Q2_1_2-read-only.txt)用分数幂多项式、每人平均绝对残差；[Q2b源码](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B05-Q2_2_2-read-only.txt)含高阶log多项式和17参数有理函数。未读取到可核验的分组发现/验证或完整论文；复杂度本身不是优点。作者自述三等奖，UNKNOWN。
- R-B06 [README快照](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B06-page.txt)主要是题面转录，排除出建模优劣结论。

## R-B07 — 特征筛选、混合模型与序列方案

[论文仓库](https://github.com/ydchen0806/23yansaiE)；[可读LaTeX](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B07-tex-read-only.txt)。奖项UNKNOWN。

- Q1a，[代码L31](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B07-q1_a-code-read-only.txt:31)使用6mL/33% OR及发病偏移加和≤48h，论文23阳性，与Skill同数量；数量一致不证明全部实现一致。
- Q1b，LaTeX L393–427：临床、体积/位置、影像特征，23%阳性，重采样，RF/LightGBM与集成。声称99%不可作泛化证据。[代码L21–32](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B07-q1_b_model-code-read-only.txt:21)先复制阳性再由AutoML内部划分；L56输出训练集accuracy。存在重复实体进入内部验证的风险。
- Q2a，LaTeX L579–637：混合效应+BiLSTM/CEEMD，报告拟合RMSE25670.456原单位。[代码L71](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B07-q2_a-code-read-only.txt:71)确有ID随机截距模型。后续L157–171全量缩放、随机row split后又在全体X/y上评价；新实体泛化未成立。BiLSTM输入另加首次ED，不等于Skill的time-only总体曲线。
- Q2b，LaTeX L659–711：按ED预测特征重要性选10变量，含HM体积、delta_ED、位置、时点等，K-means四组，比较多个组数。不是经过验证的全轨迹形态聚类。
- [Q2b代码L55–78](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B07-q2_b-code-read-only.txt:55)在first_data合并表上选特征/聚类，再拟合全部组内行；L104–105在训练X/y上评价。L106、L115先逐点平方开根再均值，其汇总实际为MAE，而论文表称RMSE；数值来源与指标定义不能直接对齐。
- Q2c/d，LaTeX L775–787：将独立样本t检验称“因果推断模型”，提出ACF/PACF，却没有不规则访视和时序方向的充分核验。仅t检验不支持因果，ACF名称不证明捕获了HM→ED的滞后关系。
- Q3a，LaTeX L943–964：80/20按ID；全变量vs前10变量的DeepForest测试accuracy0.45→0.55、训练0.85→0.87。可学的是把特征删减作为显式比较；不能照搬筛选阈值或声称10变量保证优越。
- Q3b，LaTeX L966–1003：带时间间隔、随访影像的LSTM，作者表称测试accuracy0.975。[代码L55–67](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B07-q3_b-code-read-only.txt:55)按ID组序列、截前5次、展平、全量PCA后才split，CONFIRMED UNSUPERVISED PREPROCESSING LEAKAGE。代码未见90天过滤；前5次不是时间cutoff，REFERENCE LEAKAGE RISK（确切>90天使用未核实）。展平PCA后传2D输入，不能只凭LSTM名称保证保留每患者时间轴；此代码也不足以复现论文所称两轮top10比较。
- Q3c，LaTeX L1005–1143、[源码L30](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B07-q3_c_LightGBM-code-read-only.txt:30)：相关性、重要性表、临床解释。其优点是给出可核查因素输出；特征importance及置换波动不是因果证据，也不替代实体级不确定性。

## R-B08 — 明确的降维思想与边界反例

[原参赛PDF](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B08.pdf)；[仓库](https://github.com/TCPtcp/Prediction-of-Hemorrhagic-Stroke-Risk)。作者自述三等奖，队号/身份无法官方匹配。README明确代码经过2025复盘，本轮只以原PDF判断原方案。

- PDF pp.7–8：核对sub074流水号，并列出4名48h内没有复查的患者；却把sub052的48.90h手动改成48.00h。这不是合法观测边界处理。当前Skill也不能把这4人的“未观察到扩张”升级为已证实阴性。
- pp.8–15：n=100、p=73，先按Spearman p<0.1筛至7变量，再70/30切分，比较RF/NN/SVM。表称RF测试accuracy0.8、F1=0.775。描述顺序提示全量筛选泄漏风险；F1平均方式不明，公式Recall还出现TN，不能按正类F1直接比较。
- pp.18–24：总体三次多项式；静态个人/病史混合类型两步聚类四组，BIC/轮廓评价，再比较线性、多项式、指数、高斯。组别34/17/31/18人；非轨迹形态聚类。各组拟合R²仅约0.13–0.22，原文自身也不是“优秀预测性能”证据。
- p.24：明确治疗实际时点未知；随后却将末次−首次体积下降认作治疗有效。这正说明时序意识不能替代claim gate。
- pp.31–35：保留前两次随访、去共线性/相关筛选、12指标、RF分类；承认mRS顺序并尝试回归取整，最后仍选nominal分类。没有QWK/Within-One-Level；Q3a与Q3b分数未清楚拆开，也没有90天cutoff证据。
- pp.35–40：相关图、岭回归系数、临床建议；比没有Q3c输出更完整，但没有验证解释稳定性；单个“输入都为1”的预测不能证明模型质量。

## What the evidence does and does not establish

1. 多个独立来源展示曲线候选比较、去冗余/特征筛选、多个特征的患者分组和明确的因素输出，这些是可借鉴的建模工作。
2. 未找到足以证明DTW、functional clustering或growth mixture优于baseline分组的可信同题结果。大多数已读来源使用静态特征；不能制造“获奖论文普遍使用完整轨迹”的共识。
3. 当前方案缺少特征组消融的证据是直接可查的；参考支持的是开展此类比较的必要性，不是任何一组数字的可信优越性。
4. 本轮没有同数据版本、同目标定义、同预测场景、同split、同指标口径且无泄漏的跨方案数值对照。所有外部成绩均为作者报告、NOT DIRECTLY COMPARABLE。
