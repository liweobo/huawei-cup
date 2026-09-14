# Evaluation Metrics

指标必须与题目目标、误差代价、数据切分和结论用途一致。

## Regression

MAE、MSE、RMSE、MAPE（零值政策）、R²；同时说明单位、尺度和外推边界。

## Classification

Accuracy、加权与宏平均 Precision/Recall/F1、Balanced Accuracy、ROC-AUC、混淆矩阵；二分类补充正类 Recall、Specificity、PR-AUC，概率任务补充 Brier score 与校准说明。类别不平衡时报告类别分布、正类流行率、多数类基线、Macro F1、Balanced Accuracy、少数类 Recall 和代价相关指标，不单独用 Accuracy 下结论；PR-AUC 必须结合正类流行率解释。

## Clustering

Silhouette、Calinski-Harabasz 越高越好，Davies-Bouldin 越低越好；必须结合随机种子、尺度和业务解释。

## Optimization / Decision

目标值、约束违约、可行率、资源利用、稳定性、场景损失、Pareto/排名稳定；不能只报目标函数。

## Ranking

排名、贴近度、秩相关、权重/新增方案扰动下稳定性；权重和标准化规则需可追踪。

## Time Series

按时间滚动/回测；报告预测跨度、MAE/RMSE、区间覆盖和基线差异，不能随机打乱替代时间验证。
