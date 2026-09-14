# Prediction Model Family

## Candidates

Naive/均值、季节性 Naive、线性/正则回归、统计时间序列、随机森林、Boosting、组合与残差修正。

## Fit

连续目标或未来状态可定义，特征在预测时可得，切分能尊重时间/组结构。时间序列优先滚动回测；表格数据先确认独立性或分组结构。

## Baseline / Primary

Naive、均值或线性回归通常是 Baseline；经一致协议验证的统计模型、树集成或组合模型才可作 Primary。XGBoost/深度模型不因名称自动升级。

## Data / Validation

记录目标时点、预测跨度、滞后、外生变量、缺口、频率、缺失策略和未来可得性。报告 MAE/RMSE/MAPE/R² 或区间覆盖，并保留回测起点。

## Common Misuse

随机打乱时序；全量拟合预处理；用未来字段；只报最好窗口；把高拟合写成因果或外推能力。
