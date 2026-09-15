# Feature Engineering Comparison

唯一Top-1候选是 **VALIDATION_SAFE_FEATURE_SET_DESIGN_AND_ABLATION**（在合法验证内设计、筛选并消融有意义的特征组）。它针对已观察到的建模过程不足；不以参考高分为效果保证，也不是增加某个模型库。

## 已有表示与参考表示

| 特征维度 | 当前方案 | 参考的实质思路 | 对标判断 |
| --- | --- | --- | --- |
| 原始临床变量 | 年龄/病史/治疗等；拆分收缩压、舒张压 | B03/B07/B08同样有临床变量；部分把年龄/血压粗分箱 | 当前不是纯粹盲喂原表；任意分箱不必更好 |
| Volume / ratios / location | Q1/Q3a含首次HM/ED和位置比例 | B03公开代码把volume×位置比例变成局部绝对负担；B07/B08选择部分位置指标 | “比例与绝对量是否提供不同信息”可泛化；具体脑区组合为G2，不能hardcode |
| Shape / intensity | Q1/Q3a已有表3形状与一阶灰度；存在join缺失 | B04 72输入；B08筛形状/灰度后保留少量指标；B07importance比较 | 不能声称Skill缺radiomics。缺的是覆盖核对、冗余处理和有验证的贡献判断 |
| 维度与去冗余 | 正则化Logistic已有容量控制；未见显式特征组/缩减方案比较 | B08 Q1 73→7，Q3去共线性与相关筛选；B07 all vs top10 | 正则化可能已足够；需要同split检验，而不是默认筛选一定优于全变量 |
| 交互/非线性变换 | Association有log-time、平方、time×exposure；预测侧候选构造有限 | B01用高斯参数概括形态；B07重要性与序列分支；部分文献只换模型名 | 有目标的表示与参数解释可学；不要求盲增交互、群智能或高容量算法 |
| 时间变化 | Q3b有first/last/max/change/slope与visit count，先90天过滤 | B03各次值及时间间隔；B07差值/相对变化、时间间隔；B08前两次随访的多模态信息 | 当前已有有效摘要，不能写成完全没有纵向特征。缺少非线性形态/时间表示的增量证据 |
| 静态+纵向融合 | Q3b重新用clinical+体积汇总，未保留Q3a完整首次shape/intensity/location | B03明确静态分支+时序分支；B07/B08保留影像多视图的意图 | **直接缺项**：当前Q3a→Q3b比较同时增随访、减首次特征，无法干净解释随访价值；不需模仿其神经网络即可改进 |
| Q2b患者表征 | 首次ED一维三分位 | B01/B04/B08主要静态多维分组；B07重要性选变量，B03各次体积描述但对齐不清 | baseline合理；缺候选表示/分组画像与合法收益比较。没有证据证明“完整轨迹聚类”已是这些来源普遍标准 |
| 可用性和变换拟合范围 | 已有Temporal/Group/ordinal/imbalance gates | B03全量SMOTE、B07全量PCA、B08先筛选再split描述 | 当前纪律应保留；学习表达思想不接受来源的泄漏实现 |

## 为什么不是“只会把原始字段直接喂模型”

[I01/I09/I10]见[冻结方案](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/current-skill-solution.md)：当前已经完成血压拆分、多表join、位置比例、形状/灰度、实体级体积变化与斜率，还有Q2关联模型的时间交互。遗漏集中于**如何形成少量有目的、可解释且可比较的特征集合，并保存它们的增量价值**。本轮不能从一道题推断该Skill在所有任务上都不会特征工程。

## 唯一下一阶段候选的边界

候选应把问题目标、变量含义、信息可得时点、样本/维度约束，与特征组的选择理由连起来；再在完全相同的训练实体、cutoff、folds和指标口径下，比较少量预先说明理由的集合。学习型筛选和表示必须在训练fold内；外层验证评估整个选择流程，不能反复窥视同一holdout。

对随访增量，应在Q3b同一合法预测场景内比较“完整首次基线”与“该基线+可用随访摘要”；不要把Q3a和Q3b不同预测时点的两个分数直接相减。保持同一模型可以分离表示收益与模型容量收益；没有收益就保留简单baseline。此处只是下一阶段验收方向，本轮没有建立契约、规则、workflow、特征或模型。

参考支持：[B07 LaTeX L943](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B07-tex-read-only.txt:943)与[B08 PDF pp.8–10、31–35](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B08.pdf)均显式比较/论证特征缩减；[B03 L968](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/sources/R-B03-tex-read-only.txt:968)提出保留静态信息再融合随访。它们的数值验证不足，所以支持“应该做受控比较”，不支持复制top10、p<0.1或某种网络。
