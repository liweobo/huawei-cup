# Validation Design Comparison

本页区分行为正确性与建模质量。证据入口：[冻结方案](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/current-skill-solution.md)、[参考原文定位](C:/Users/aaa/Desktop/test/huawei-cup-2026/development/artifacts/2023e-reference-benchmark/source-notes.md)。严谨协议提高可信度，并不自动提高预测成绩。

| 维度 | 当前Skill已有证据 | 已读参考材料 | 判断 |
| --- | --- | --- | --- |
| 样本单位 | Q1/Q3聚合后一实体一行；Q2为100实体/450行 | B01/B04多为总体曲线拟合；B07 Q2有mixedlm但后续row split；B08用患者静态表分组 | 重复观测不能当450独立人。不能对所有静态表机械要求GroupKFold |
| Holdout / K-fold | 原Q1 5-fold、Q3 4-fold；升级测试代码为5×2 / 4×2重复分层CV | B03 80/20+10/15折调参；B07/B08多为单次80/20或70/30，部分训练精度 | 协议更可追溯是SKILL ADVANTAGE；升级数字缺持久副本仍是证据限制 |
| Grouped validation | Q2a实际5折80/20实体，overlap全部0；Q2b分界和曲线fit IDs被检查 | 未找到可核验的新实体OOF曲线/分组评价；B07 Q2a代码随机拆行并评价全体 | SKILL ADVANTAGE；mixed model名称不等于完成grouped预测验证 |
| 时间可得性 | Q3聚合前过滤>2160h；原9行/8人泄漏证据保留失效 | B03“全部影像”；B07截前5次，B08前2次；未给90天/统一cutoff证明 | REFERENCE LEAKAGE RISK。没有断言参考必定用了同样9条；90天过滤也不证明Skill具有固定早期landmark能力 |
| 预处理与无监督步骤 | 插补/缩放在CV pipeline；Q2b每fold单独学习分界 | B03 Q1全量缩放/SMOTE先于CV；B07 Q3b全量PCA先于split | 确认的代码泄漏不能降格为一般warning；这些分数不得作为可信基准 |
| 分组发现 | 验证者只用预测时可得baseline赋组；baseline回预测不计未来分数 | B03/B07全体选择特征/簇并拟合；B01/B04/B08仅作全体描述 | 全数据描述性聚类本身不自动叫泄漏；只有冒充新实体/未来验证才违法。回顾性形态描述与可部署赋组必须分开 |
| Model selection | 要求同scope/split/metrics；实际曲线仍是固定候选，非充分方法比较 | B03调参后在同一CV矩阵报分；B07特征/簇数主要靠拟合误差 | Skill的比较规则正确，但建模候选与表征比较仍不足；不能把规则存在当实验已完成 |
| 类别不平衡 | PR-AUC、少数类Recall、Balanced Accuracy、多数类baseline；fold内处理 | B03使用SMOTE但顺序错误；B08的F1汇总/Recall口径不清 | SKILL ADVANTAGE；高accuracy不代表识别扩张 |
| Ordinal | cumulative ordinal及MAE/RMSE/QWK/Within-One-Level协议 | B03/B08有顺序意识；B07仍nominal交叉熵；多只报accuracy | SKILL ADVANTAGE是目标与指标对齐，未证明升级模型实际更准 |
| 概率/校准 | Q1测试定义Brier等；未保存可靠性曲线或外部校准结果 | 已读来源没有充分校准证据；将神经网络输出缩至0–1不等于校准 | 双方都不能宣称概率已可靠校准 |
| 估计不确定性 | association按实体CR1、t(99)名义CI；group bootstrap规则存在，未进行本轮bootstrap | B08给曲线参数95%CI，B07有importance波动；未见统一实体抽样CI | 确认相关结构是优势；名义CI不证明因果/多重检验控制，CV折间std不是CI |
| Robustness / sensitivity | 已明确留后续阶段，未声称完成 | B07有特征数量/簇数量图，但多基于同一拟合数据 | 记录范围及不足，不把“有敏感性图”当稳健性证明；本轮不实施 |

## 既有Q2a row-vs-group对照

本轮仅读取之前的I07，未重训。相同time-only二次Ridge、100实体450行：

| 原有协议 | pooled OOF MAE (mL) | RMSE (mL) | R² | 可信状态 |
| --- | --- | --- | --- | --- |
| Patient/entity-grouped 5-fold | 19.801187 | 26.229155 | −0.012561 | 合法新实体评价，仍显示预测能力弱 |
| Row-random 5-fold | 本页不额外补数 | 26.344805 | −0.021510 | INVALIDATED；每fold重叠实体58/60/58/62/59 |
| 全100实体最终拟合 | 不作为OOF成绩 | 25.965972 | 不作为OOF成绩 | FIT_RESIDUAL |

这次row-random没有更优RMSE，不能捏造“泄漏必然让本次分数大幅上升”。禁止该协议的理由是独立性失效，而非分数方向。最终拟合残差也不等于验证误差。

## 数值是否可以排名

全部外部对照为 **NOT DIRECTLY COMPARABLE**：

- B03 Q1目标由曲线求根，且SMOTE先于CV。
- B07 Q1报告训练/内部评价；Q2加入首次ED，评价包含训练数据；Q2b某代码路径将MAE称为RMSE。
- B01/B04/B08曲线主要报告拟合；残差可能是每人绝对和、均值或不同缩放单位。
- B07/B08 Q3缺一致cutoff、同fold和完整预处理隔离证据；B08未清楚区分Q3a/b指标；不能与Skill corrected OOF/QWK相比。
- 即使文件来源都是2023E，也还需要处理后的数据、标签、可用时间及metric aggregation相同，才有数值优劣意义。

当前Skill的Brier/ordinal升级指标只在既往测试stdout输出，未找到持久副本。本轮不复跑填补；旧套件通过仅证明行为回归，当作历史证据引用。
