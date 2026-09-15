# Question-by-Question Comparison

Skill事实来自 [冻结摘要](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/current-skill-solution.md) 的I01–I14；P01–P10均是事后参考，详见 [逐篇页码记录](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/source-notes.md)。所有外部分数尚不满足同数据版本、目标和验证协议三个条件，均为 **NOT DIRECTLY COMPARABLE**。

| Question | Skill Approach | Common Reference Approaches | Skill Strength | Skill Weakness | Generalizable Gap? |
| --- | --- | --- | --- | --- | --- |
| Q1a | onset重建、≤48h、首次HM增量≥6mL或≥33%、第一次观测命中；23/100 | 多数采用时间偏移与逐次阈值；P05 p14取最大值时点；P10 p13公式用相邻差；P08 p9逻辑式不一致 | 阈值、单位、时序可追溯，不照抄参考标签 | 4例窗口内无随访仍记0；首次观测非精确发生时刻，异常次序验证不足 | 记录观测限制，不另立G1 |
| Q1b | 首次clinical+volume/location+shape/intensity；多数类、正则/加权Logistic、浅RF；重复分层CV | P01 p19特征消融；P03 MI/RF筛选；P08分域融合且选Logistic；P09因子分析；P06适度RF分数 | 少数类指标、PR-AUC/Brier、fold内预处理；不用模型名评分 | 高维小样本，缺特征组比较；升级分数未持久化，不能证明强预测 | **G1：特征集设计与合法消融**；原因E，数据难、表示不足与验证差异共同作用 |
| Q2a | time-only quadratic Ridge；100实体450行；grouped RMSE26.229mL/R²−0.0126；final fit另报 | P02 LOESS/指数二次；P03/P04/P09 Gaussian/poly；P07分段；P10 log-time RBF/spline | FIT_RESIDUAL≠VALIDATION_ERROR；group overlap=0；row对照没有更乐观也如实保留 | 固定曲线无候选选择证据；非负、远期外推与形态限制未充分处理 | 现有主模型比较原则的执行不足，不因曲线名另立G1 |
| Q2b | baseline ED tertiles34/33/33；fold内学边界，验证实体用baseline赋组 | 静态3篇、按记录2篇、实体形状2篇、表示不充分3篇；P06 DTW距离表示，P10阶段斜率 | 新实体赋组与训练隔离清楚，是可部署baseline | 相同起点不同走势无法区分；缺表示比较和轨迹画像 | **同一G1的纵向表示实例**；不直接要求完整轨迹聚类模块 |
| Q2c | 等实体权WLS、CR1区间、crude/adjusted、time×treatment；时序UNKNOWN | P02/P05实体斜率回归，P06趋势检验，P09混合效应动机但实际表不支持；灰色/树/案例 | 暴露时序、稀有组、混杂与关联措辞纪律更严格 | 严重程度和共同治疗未充分控制；区间探索性 | G3：mixed/GEE/WLS方法差异；G4：参考因果越界；不新建因果模块 |
| Q2d | 同次HM变化与ED变化的条件关联；100实体350随访；HM每10mL关联3.639mL | 均值/末次变化相关、回归、树；P01案例滞后图；P09名义混合模型 | HM同次变量不冒充处理前confounder；单位、区间清楚 | 无lag辨识或跨设定稳定证据 | 领域动态假设属G2；未见共同证据要求joint/lag模型 |
| Q3a | 首次完整多视图；nominal vs cumulative ordinal；4×2CV；MAE/RMSE/QWK/Within-One | 多篇筛选+树/网络/回归；P06邻近命中；P07有序Logit在Q3c | 序数目标、距离指标、稀疏等级与训练隔离是优势 | 升级分数未留档，特征组贡献未验证，不能宣称ordinal已获胜 | **同一G1**；不用XGB不构成缺口 |
| Q3b | ≤2160h后每实体first/last/max/change/slope；未合并完整Q3a影像基线 | 8篇保留baseline再加随访；P01/P05/P06时间摘要；P09 baseline21+末次105→28；P10序列模型 | 原9行/8人超90天泄漏仍INVALIDATED；先截断再聚合 | 基线信息丢失使随访收益不可归因；缺转折表示；90天horizon不是统一早期landmark | **最直接G1证据**；不复制参考的无cutoff全随访 |
| Q3c | 因果措辞gate存在；无持久化独立mRS因素排序产物 | 相关/重要性/检验/领域画像；P03混杂提醒；P07有序解释但权重有问题 | 不把ED关联冒充mRS因素，不把importance写成因果 | 本次交付缺项；解释排序和稳定性未完成 | run完成度不足，不自动推断通用Skill缺新模块 |

等级：Q1 ADEQUATE；Q2 WEAK；Q3 WEAK；Overall NEEDS_MODELING_IMPROVEMENT。针对已保存建模产物的深度和完整度，不把安全测试通过当作竞赛高分。
