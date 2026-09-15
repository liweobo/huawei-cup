# Validation Design Comparison

范围：已冻结独立run及其定向升级，对比P01–P10参赛稿。参考数字均为作者报告，本轮不复现，不用不可比分数判输赢。

| Aspect | Current Skill evidence | References | Assessment |
| --- | --- | --- | --- |
| Training fit vs validation | I07独立保存FIT_RESIDUAL与VALIDATION_ERROR | Q2主要fit residual；P01附录pp55–56/59、P09附录p71明确有训练集评分 | **SKILL ADVANTAGE**：能区分拟合与泛化；不代表泛化已经好 |
| Holdout | 当前Q1/Q3使用重复CV协议 | P05/P06/P08/P09等单次70/30、80/20或其他比例；有些正文称CV而实现不一致 | 样本小，单次高分不足以建立优越性 |
| K-fold / repeated CV | I09 Q1 5×2；I10 Q3 4×2、最少等级4人；升级分数stdout未持久化 | 多篇提K-fold；P10 p19 Logistic Kfold、RF/XGB holdout混比 | Skill协议较完整；不能用代码存在代替升级性能结果 |
| Grouped CV | I07 Q2a每fold80/20实体，overlap全0；Q2b训练fold内边界 | 0/10建立了同等级可核验的新实体Q2验证 | **SKILL ADVANTAGE**；仅未报告时标unverified，不断言group leakage已发生 |
| Temporal validation | I01/I10先排除>2160h再聚合；历史9行/8人泄漏失效保留 | 0/10明确证明Q3b逐记录目标前cutoff；P09取last、P02展开、P10全序列 | **SKILL ADVANTAGE**；当前90day上界仍不等于统一早期landmark或前瞻验证 |
| Preprocessing isolation | 当前插补、缩放、编码在fold；新group gate含PCA/聚类 | P07 p78确认SMOTE先于split；其他全量筛选/缩放常未交代隔离 | 既有gate不得因参考高分放松 |
| Calibration | Q1指标协议含Brier；无持久化校准曲线与决策阈值结果 | 主集合没有可核验的系统性校准验证报告；输出概率不等于校准 | 双方证据不足，不宣称Skill已完成calibration |
| Confidence interval | I08按实体CR1与t(99)的nominal区间 | P04/P05/P09曲线参数区间；P08预测带；其独立性假设未核验 | 不同区间目标不可混比；Skill的聚类区间也不是因果区间 |
| Bootstrap / effective n | Group-aware能力要求相关重复记录按实体；未见此次Q2/Q3完整bootstrap产物 | 未建立可核验的实体bootstrap方案；P07按均体积加权序数汇总有伪样本量风险 | 规则优势与本题实际不确定性证据应分开 |
| Sensitivity / uncertainty | 已有通用workflow，但2023E建模仍未完成整体robustness/sensitivity | 多篇有局限/参数扫描/曲线阶数对照；没有形成可直接比较的完整稳定性协议 | 不将调参自动当稳健性；本轮不修复，也不选为Top-1 |

## 已有Q2a row-vs-group事实

| Protocol | RMSE mL | MAE mL | R² | Usage |
| --- | --- | --- | --- | --- |
| Row-random | 26.344805 | 见I07原始结果，不补造 | −0.021510 | INVALIDATED对照；每fold共享58/60/58/62/59实体 |
| Patient-grouped | 26.229155 | 19.801187 | −0.012561 | 正式新实体评价；五fold全零重叠 |
| Full-data final fit residual | 25.965972 | 非外部验证 | 非外部验证 | 题目所需FIT_RESIDUAL |

本次row随机分数没有更好。不能为了证明泄漏危害而改写结果，也不能因差值小就允许实体重叠。合法性和实际乐观幅度是两个判断。

## Numeric comparability register

| Proposed comparison | Decision | Why |
| --- | --- | --- |
| Skill旧Q1 AUC0.575381 vs P06 AUC0.7031/P07 AUC0.85 | NOT DIRECTLY COMPARABLE | 原/升级版本不同，cohort/标签/切分/重采样不同；P07存在split前SMOTE |
| Skill grouped RMSE26.229mL vs P09 fitRMSE6.90 | NOT DIRECTLY COMPARABLE | 独立实体OOF vs训练拟合；输入筛选、残差和数据版本未一致 |
| Skill Q3 nominal MAE1.42/QWK0.342714 vs P06/P09 accuracy或P10 RNN98% | NOT DIRECTLY COMPARABLE | 指标、输入、cutoff、样本/验证与模型版本不同 |
| Skill Q3a→Q3b已有分数差 | 不能干净归因为新增随访 | Q3b同时丢失完整基线影像特征集；不是固定输入基线的增量比较 |
| P06 baseline→followup或P09同模型前后结果 | 可记录作者内部比较思想；不接受为已验证改进幅度 | 是否相同fold、选择隔离、时间边界未证实 |
| 模型A row CV vs模型B group CV | 禁止排名 | validation estimand不一致 |

本轮没有找到满足三项可比条件的外部性能对。没有推算“差多少分”或预计提升百分比。
