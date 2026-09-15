# Current Skill Solution — frozen before reference reading

Scope: 2023E；基准代码提交 cce0a80d03aef5ec69713cac5afa85cb154933b7。此文在第一次互联网检索及参考方案阅读前形成，冻结后不根据参考论文改写。原 run 是 BLIND RUN；后续定向能力验证仍与本次 POST_HOC REFERENCE 分开。

原始 run 的状态是 SECOND_PROBLEM_BASELINE_COMPLETE / DIAGNOSTIC ONLY，不是已完成比赛论文或提交表。当前能力包含后续 Group、Ordinal、Imbalance 与 Association 升级，但不能把升级反写为原盲跑时已经具备。

## Existing evidence

| ID | 现有 artifact / source | 用途 |
| --- | --- | --- |
| I01 | [clinical_baseline.py](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/benchmarks/runtime/historical_2023_e_hemorrhagic_stroke/run-001/code/clinical_baseline.py) | 冻结实现：时间恢复、标签、拼表、基线和聚合 |
| I02 | [run_summary.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/benchmarks/runtime/historical_2023_e_hemorrhagic_stroke/run-001/outputs/run_summary.json) | 人数、标签数与原模型列表 |
| I03 | [baseline_metrics.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/benchmarks/runtime/historical_2023_e_hemorrhagic_stroke/run-001/outputs/baseline_metrics.json) | 原盲跑 Q1/Q3 可追溯数值 |
| I04 | [q1_expansion_labels.csv](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/benchmarks/runtime/historical_2023_e_hemorrhagic_stroke/run-001/outputs/q1_expansion_labels.csv) | 扩张判断、时间及 48h 内随访数 |
| I05 | [data_audit.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/benchmarks/runtime/historical_2023_e_hemorrhagic_stroke/run-001/outputs/data_audit.json) | 时间覆盖、shape join、类分布 |
| I06 | [q2_summary.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/benchmarks/runtime/historical_2023_e_hemorrhagic_stroke/run-001/outputs/q2_summary.json) | 原 Q2 曲线、分组及未调整 slope 比较 |
| I07 | [Group targeted results.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/grouped-longitudinal-validation/q2-targeted/results.json) | 后续 Q2a grouped 评价、Q2b fold 内分组检查 |
| I08 | [Association results.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/observational-association/q2-targeted/results.json) | 后续 Q2c/Q2d 观察性关联 |
| I09 | [Q1 imbalance targeted test](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/tests/test_2023e_imbalanced_q1.py) | 当前 Q1 候选、重复 CV 与指标协议 |
| I10 | [Q3 ordinal targeted test](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/tests/test_2023e_ordinal_q3.py) | 当前 Q3 nominal/ordinal 比较与时间检查 |
| I11 | [reviewer-diagnostic.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/benchmarks/runtime/historical_2023_e_hemorrhagic_stroke/run-001/reviewer-diagnostic.md) | 首次失败：9 条超 90 天记录；失效证据保留 |
| I12 | [current-evidence.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/benchmarks/runtime/historical_2023_e_hemorrhagic_stroke/run-001/work/current-evidence.md) | 原 run 未看外部论文、未写答案表的声明 |
| I13 | [Association completion.json](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/observational-association/completion.json) | 226 pytest + 20 harness 已通过；不等于模型预测质量高 |
| I14 | [competition-state.md](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/benchmarks/runtime/historical_2023_e_hemorrhagic_stroke/run-001/competition-state.md) | 原 run 为诊断状态，未选主模型、未写完整论文 |

I09/I10 的定向测试在此前测试套件中运行通过；它们只向 stdout 打印逐模型数值，不写 run artifacts。本轮在项目现有 JSON/MD/TXT/LOG 中没有找到这些 stdout 的持久副本。因此下面如实记录升级的方法与协议，不补造升级后的数值，也不在本轮重新训练以补数。

## Q1a

- **Problem interpretation**：发病后 48h 内，相对首次影像的 HM 增加达到 6 mL 或 33%，记录第一次观测到满足条件的时间。
- **Features**：表 1 的发病到首次影像小时数；附表流水号到真实影像时间映射；表 2 各次 HM。
- **Model**：确定性规则；原单位 10^-3 mL 对应阈值 6000；使用 ≤48h、≥6000 或 ≥0.33。按重建时间排序，取第一个 hit。
- **Validation**：时间映射覆盖 593/593 个表 2 流水号；缺失或非正 baseline HM 标为 missing_baseline_volume；保留 within48_followups 和 label_status。
- **Metrics**：不是分类拟合分数；报告规则标签数和观测时刻。
- **Result**：100 人中 23 阳性、77 阴性；阳性首次观测扩张时间 6.5417–42.7567h。[I01–I05]
- **Limitations**：4 人在 48h 内没有后续影像，原代码仍将“未观察到 hit”编码为 0；这不证明其期间绝无扩张。首次观测满足阈值的时间不是生物学精确起始时间。时间基准在原代码取该实体最早 timestamp，再回填首次检查间隔；未提供异常次序的独立压力测试记录。

## Q1b

- **Problem interpretation**：仅首次可用信息预测扩张概率，训练为 100 人，输出到 160 人；没有 60 人的公开测试标签。
- **Features**：临床/病史、拆分后的收缩压/舒张压、首次 HM/ED 体积与部位比例、首次表 3 Hemo/ED 形状与灰度分布；并非只用临床原字段。ID、目标及随访被排除。
- **Model**：盲跑为 C=0.2 的 class-balanced logistic 与浅随机森林；当前 I09 另比较 regularized logistic、class-weighted logistic、浅 RF。
- **Validation**：盲跑 5-fold stratified OOF；当前 I09 是 5-fold×2 repeats、seed=42。插补、缩放和 one-hot 在 pipeline 内拟合；一患者一行。按 PR-AUC 比较当前候选，不按 accuracy 排序。
- **Metrics**：当前包括 ROC-AUC、PR-AUC、Balanced Accuracy、Recall、Precision、F1、Specificity、Brier 及折间波动。
- **Result**：持久化盲跑 logistic ROC-AUC=0.575381、Recall=0.217391、Balanced Accuracy=0.472332；RF ROC-AUC=0.467532、Recall=0。多数类 accuracy=0.77，不能据此称模型好。当前重复 CV 候选逐模型数值未持久化，不能用原分数冒充升级分数。[I01、I03、I09]
- **Limitations**：n=100、阳性 23，高维且缺少有验证依据的特征筛选/非线性构造；shape joins 存在覆盖不足，影像多视图主要是直接拼接。缺少校准验证图、外部测试和确定的临床决策阈值；治疗标记在“首次可用”时的真实可得性仍不明确。

## Q2a

- **Problem interpretation**：全体 100 人的 ED 随发病后时间曲线，并计算 observed−fitted 残差；另外评价对未见实体的预测。
- **Features**：onset-to-imaging hours；100 实体、450 行；每实体 3–9 次、median=4。
- **Model**：固定 time-only 二次 Ridge，alpha=1；t 以训练 fold 的 median/std 标准化。最终全体拟合 f=26749.989596+977.356402z−466.967597z²，z=(t−63.921806)/549.738102；体积为原始单位。
- **Validation**：后续 5-fold GroupKFold，80/20 实体，全部 overlap=0；row-random 仅为 INVALIDATED 对照。模型形式固定，未做曲线族搜索。
- **Metrics**：observation-weighted pooled OOF MAE/RMSE/R²；FIT_RESIDUAL 与 VALIDATION_ERROR 分开。
- **Result**：grouped MAE=19.801187 mL、RMSE=26.229155 mL、R²=−0.012561；row-random RMSE=26.344805 mL、R²=−0.021510，每 fold 共享 58/60/58/62/59 实体。最终 in-sample residual RMSE=25.965972 mL。[I06、I07]
- **Limitations**：time-only quadratic 的独立实体预测不优于该 pooled R² 的均值基准；不能称泛化好。未比較 spline/GAM/piecewise 或其他合理曲线族，未建个体曲线或生理约束。row 对照本次没有稳定的分数优势，不构成允许 row leakage 的理由。

## Q2b

- **Problem interpretation**：发现 3–5 个亚组并给出各组 ED 轨迹与残差。
- **Features**：首次 ED 一维值；后续 ED 只用于组内曲线。
- **Model**：baseline ED tertiles 三组；全体原阈值 8.178、16.801 mL；各组二次 Ridge。
- **Validation**：当前 I07 的 minimal test 在每 fold 的 80 个训练实体内拟合分界和组内曲线，再以验证实体的 baseline 赋组；反例与 fit IDs 检查通过。只计 350 条后续记录，不把 baseline 当未来预测。
- **Metrics**：最小测试重点为 group separation、fold 内 discovery、边界与训练曲线参数隔离；没有保存跨多种亚组发现方法的质量比较。
- **Result**：全体基线分组为 34/33/33 人；5 folds 的全量边界反例都被拒绝。subgroup_count_optimized=false。[I02、I06、I07]
- **Limitations**：是可解释起点；相同 baseline、不同进展形状的实体不会被区分。没有 trajectory representation、shape-based grouping、组稳定性或可解释的异质进展比较证据。不能称已经完成成熟的纵向亚组发现。

## Q2c

- **Problem interpretation**：七种记录治疗与 ED 进展的观察性关联。
- **Features**：episode-level 治疗标记、固定 log-time 及平方项、每治疗一个 time interaction；调整年龄、性别、既往高血压。
- **Model**：原盲跑是每患者 ED 直线 slope 的组间均值差；当前 I08 为每实体总权重 1 的 WLS，crude vs adjusted，同样本比较；CR1 实体聚类协方差、t(99) nominal 区间。
- **Validation**：估计层面处理实体依赖，未声称新实体预测得分；暴露 prevalence、21 对共现、初始差异和时序已审计；实际治疗时间 UNKNOWN。
- **Metrics**：接受组减未接受组的第 7→28 天拟合 ED 变化差（mL），nominal 95% CI；不是 treatment effect。
- **Result**：调整后差异：引流 −7.936、止血 −2.080、降颅压 +6.843、降压 +7.153、镇静镇痛 +2.977、止吐护胃 +5.798、营养神经 −3.154 mL。引流、降压、止吐护胃、营养神经因一侧少于 10 人标 ESTIMATE_UNSTABLE。[I08]
- **Limitations**：治疗时序未知、急性治疗前严重程度及共同治疗未充分控制；不能作因果/获益/危害解释；区间探索性、未作多重比较校正。

## Q2d

- **Problem interpretation**：HM、ED 变化及治疗的联合条件关联。
- **Features**：ED 相对首次的变化为 outcome；首次 HM/10mL、同次 HM 变化/10mL 为联合测量变量；降颅压和止血按组支持度与共现选择；另加固定时间及三项处理前调整。
- **Model**：100 实体、350 条随访；equal-entity WLS、CR1 聚类区间；调整模型 12 参数。HM 变量明确不是已核验的普通治疗前 confounders。
- **Validation**：先核验测量在本次 outcome 时或之前可得；未声称干预时序或动态预测已验证；无模型搜索。
- **Metrics**：crude/adjusted coefficients 和 nominal 95% CI。
- **Result**：同次 HM 变化每 10mL 的 crude 关联为 3.426 mL，adjusted 为 3.639 mL，CI [1.604,5.675]；首次 HM adjusted=0.057，CI [−1.061,1.175]。治疗条件轨迹差：降颅压 +10.880，止血 −4.478 mL。[I08]
- **Limitations**：没有 lag/cross-lag 动态识别；共同变化不能支持方向或因果解释；只能说明两种指定设定中的关联，未做跨设定稳健性证明。

## Q3a

- **Problem interpretation**：首次信息预测 90-day mRS 0–6，有序目标；训练 100 人，预测 160 人。
- **Features**：同 Q1b 的临床、首次体积/部位、shape/intensity；无随访。
- **Model**：盲跑 class-balanced multinomial logistic；当前 I10 比较 nominal multinomial 和 CumulativeOrdinalLogistic，C=0.2，另有 median baseline。
- **Validation**：原 4-fold stratified OOF；当前 4-fold×2 repeats，seed=42，fold 内预处理；最稀有等级 4 人，一实体一行。
- **Metrics**：MAE、RMSE、QWK、Accuracy、Within-One-Level，当前报告 fold mean/std。
- **Result**：保存的盲跑 nominal MAE=1.53、RMSE=2.056696、QWK=0.230461、Accuracy=0.25；当前 ordinal 升级通过定向测试，但逐模型数值未找到持久 artifact，不能宣称 ordinal 已经提高成绩。[I03、I10、I13]
- **Limitations**：小样本/高维、罕见等级、无外部验证；尚无特征组消融或已验证的序数模型优势。

## Q3b

- **Problem interpretation**：对训练及有随访测试组，用已知临床/随访信息预测 90-day mRS；与首次场景分开。
- **Features**：clinical + 每实体 HM/ED first/last/max/change/全局线性 slope、visit_count、固定 2160h horizon。实际实现未把 Q3a 完整首次 shape/intensity/location 特征矩阵继续合并进 Q3b。
- **Model**：一实体一行聚合；原 nominal logistic；当前 I10 nominal vs cumulative ordinal。
- **Validation**：先过滤 >2160h 记录再聚合；原 9 条超 90 天记录（8 人）的泄漏结果保留为 INVALIDATED。原 4-fold；当前 4-fold×2 repeats。聚合后的行切分是实体切分。
- **Metrics**：同 Q3a。
- **Result**：保存的经 90 天截断 nominal MAE=1.42、RMSE=1.994994、QWK=0.342714、Accuracy=0.29；不能与升级 ordinal 数值混用，不能将原失效结果复活。[I01、I03、I10、I11]
- **Limitations**：90 天 outcome horizon 不等于统一的早期临床 prediction cutoff；没有多个 landmark 的动态预测。没有保留基线全部模态的增量比较，没有非线性 trajectory shape、time-to-peak 或不规则访视采样的完整建模。不同 Q3a/Q3b feature sets 的增量价值无法干净归因于随访信息。

## Q3c

- **Problem interpretation**：关键因素分析及临床建议应区分预测重要性、统计关联、因果因素。
- **Features**：候选历史、治疗和影像字段；Q2c/Q2d 有独立关联输出，但其 outcome 是 ED，不是 90-day mRS。
- **Model**：现有 frozen code 中未见独立 Q3c 排名/系数/SHAP/permutation 输出流程；不能把 Q2 关联或 Q3 预测自动当作 Q3c 分析。
- **Validation**：当前通用 Reviewer 可拦截未经支持的因果措辞；未见 Q3c 解释稳定性或外部临床验证 artifact。
- **Metrics**：无独立 Q3c 数值 artifact。
- **Result**：可确认预测与观察性建议的证据边界；不能确认已经完成经验证的关键因素排序。[I01、I12–I14]
- **Limitations**：这是当前已保存建模产物的明确缺项，区别于安全规范已经存在。未写完整比赛论文或答案表，不能评价不存在的最终摘要/图表为“优秀”。

## Freeze boundaries

这是对既有方案的事实摘要，不含优秀论文方法。本轮不重训、不修改原 label、模型、prediction、active evidence 或历史失效记录。指标缺失用“现有持久 artifact 未找到”标记，不用代码能力或测试通过替代实际预测数字。外部参考尚未读取；本文件及源码/历史 SHA256 的冻结时间由旁置 JSON 记录。
