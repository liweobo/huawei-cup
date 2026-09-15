# Trajectory Modeling and Longitudinal Subgroup Discovery

## Q2a Overall curve

| Source | 时间、曲线与选择 | Residual / validation / interpretation |
| --- | --- | --- |
| Skill I07 | onset小时，训练fold标准化z/z²，固定Ridge | 100实体450行；grouped OOF另于final fit；未验证替代曲线、非负和远期形态 |
| P01 pp22–25/59 | time-only tree/RF/GBDT/linear | 正文CV叙述与附录训练评分不一致；树锯齿不代表生理机制 |
| P02 pp14–18 | LOESS vs exp(二次time) | 拟合残差与升后降解释，未见新实体验证 |
| P03 pp26–38 | poly2–5、插值、Gaussian | fit R²选型；答案取首次残差，非所有随访预测误差 |
| P04 pp37–45 | 天；OLS1–7/LAR/Gaussian | 讨论尾部形态；剔除长随访者改变样本；最终曲线叙述矛盾 |
| P05 pp19–21 | ≤48h，第五阶poly | 声称48h后无分析价值，改变Q2时间范围 |
| P06 pp25–27 | 435点，poly3/4/5 | 第四阶；实体有符号残差和，无grouped OOF |
| P07 pp20–25 | 分段degree2/3/4×4种分段数 | 以mean residual选degree4/5段；复杂度收益无独立验证 |
| P08 pp21–27 | 五时段poly/Gaussian及预测带 | p27残差定义后再作比值；不等于统一残差误差，也未证明相关观测区间合法 |
| P09 pp22–27 | onset小时，LOESS双核/poly7/双Gaussian | 讨论负体积及异常远期峰；fit RMSE选型非grouped预测 |
| P10 pp20–23 | log-time，RBF/spline | 早晚尺度展示有价值；绝对残差定义后出现负表值 |

二次曲线可作为起点，**尚不足以确认最终选型**：当前合法OOF R²接近零且无曲线候选比较。不是“高斯一定优于Ridge”；参考训练拟合没有证明能改善26.229mL的独立实体误差。

## Q2b 分组对象与表示

| Category | Papers | 证据与含义 |
| --- | --- | --- |
| 静态临床表示 | P01 p28；P05 pp21–30；P07 p28 | 临床/病史/治疗；P01还含mRS；P05为age/BP。支持静态分组方法家族，非轨迹共识 |
| 展开观测/单位问题 | P02 pp18–19；P03 pp46–47 | P02复制临床/mRS提高同人归组“概率”；P03的266+100+84是450条观测。不能当完整实体亚组发现 |
| 时间形状表示明确 | P06 pp27–35/84–86 | 实体标准化、插值8点、fastdtw距离矩阵、普通KMeans作用于矩阵行；不是DTW-barycenter目标；归一化可丢失幅度和真实时间尺度 |
| 时间形状表示明确 | P10 pp24–28 | 初/中/末斜率→三维→MeanShift四组；低维趋势画像 |
| 表示不足以确认 | P04 pp45–52；P08 pp28–32；P09 pp28–37/72 | 报告实体人数和拟合曲线，但时间对齐/距离输入未充分交代；P09代码只读取已分组sheet |

互斥计数3+2+2+3=10。明确时间形状表示仅2/10，不能写“多数优秀论文都做trajectory clustering”。

Skill的baseline ED三分位是合理、可解释且可在baseline赋组的起点；但没有检验同起点不同走势，不能称充分纵向亚组发现。可借鉴的是表示假设和比较，而不是某个聚类算法名字。

完整轨迹回顾性分组与“只看baseline预测新实体未来”不是同一任务。前者可用定义窗口内的轨迹描述异质性；后者验证实体不能利用待预测随访决定组别。未来候选须先定观察窗口，学习步骤仅在训练groups内执行。本轮只记录诊断。

## Q3b Follow-up representation

| Papers | 可确认的表示 | Baseline | 时间风险 |
| --- | --- | --- | --- |
| P01 pp43–45 | recovery duration、HM/ED max、扩张持续时间 | 保留 | cutoff不清，HM阈值套ED缺依据 |
| P05 pp40–42 | 部位比例×总体积、区域相邻变化率均值 | 保留 | cutoff不清，短间隔噪声未验证 |
| P06 pp49–51 | 以距发病时间加权均值、Integrated Slope、末次/先前max | 保留 | 公式不是标准时间积分AUC；全随访边界未知 |
| P03/P04/P08 | visit wide、missing indicator/coverage筛列 | 保留 | 全随访不能自动视为早期预测可用 |
| P09 pp59–62 | baseline21+last105→126→28 | 保留 | last日期未核实，不足以安全预测90-day |
| P10 pp37–41 | baseline+wide vs padded3D RNN | 保留 | 同时改表示和模型，5000epochs/100人，cutoff不清 |
| P02 pp37–40 | 访视展开多行 | 完整保留不充分 | group与time风险并存 |
| P07 p58 | 泛称全部随访 | 不充分 | 不猜实际表示/cutoff |
| Skill I01/I10 | first/last/max/change/全局slope、count | clinical保留；完整radiomics/location丢失 | 已去>2160h；仍未构造统一早期landmark |

没有共同证据要求强制peak time、AUC、curvature、functional/growth-mixture clustering或Gaussian process。P06/P10支持可迁移的低维时间表示思路，但不证明指定公式或模型最优。优先诊断是：保留已有可用信息，比较少量可解释表示，在固定合法协议下识别增量价值。
