# 论文数字证据准入审计

审计时间：2026-09-03  
活动运行：`run-003`  
审计结论：当前没有论文正文文件；以下清单规定哪些数字可以进入论文，哪些必须保持 `NOT RUN` 或 `[需要验证]`。

## 可进入论文的真实数字

### 数据结构与附件审计

附件一四个材料工作表的行数、1028 列结构、缺失单元格、完全重复行、波形数量、温度数量、频率/损耗范围，必须引用当前 run 的 canonical audit：

- `E-DATA-AUDIT-CANONICAL-003` -> `work/data-audit-summary.json`
- `E-DATA-AUDIT-RAW-A1-003` -> `work/audit_attachment1.json`
- `E-DATA-AUDIT-REPORT-A1-003` -> `work/attachment1-data-inspection.md`

这些数字来自实际运行的只读 `data_audit.py` 扫描和同一 run 的 canonical 汇总，不是示例。异常点数只能写成“统计候选”，不能写成已确认错误或已删除样本。

### 问题一分类结果

只使用当前 Active Evidence Set 选中的 `EXP-Q1-MODEL-COMP-003` 版本：

- 训练/验证行数、26 个特征、分层 8:2 切分、Accuracy、Balanced Accuracy、Macro F1、混淆矩阵：
  `E-Q1-MODEL-COMP-RESULT-003`、`E-Q1-MODEL-COMP-TABLE-003`、对应三个混淆矩阵证据；
- 附件二 80 个样本的预测数量和逐样本标签：
  `E-Q1-MODEL-COMP-PREDICTIONS-003`。

当前实际运行的三模型验证指标均为 1.0000，附件二预测数量均为正弦波 20、三角波 44、梯形波 16。附件二没有真实标签，因此不能把 1.0000 写成附件二准确率。

### 问题四写入前的序号检查

附件三与附件四的样本序号覆盖 1--400、逐行一致，以及附件四预测列写入前为空，可引用：

- `E-Q4-ALIGNMENT-CHECK-003` -> `work/q4-output-alignment-check.md`

这不是问题四预测结果，只是写入前的真实对齐检查。

## 当前禁止写入论文的数字

- 问题二：Steinmetz 温度修正方程的系数、误差、温度效应方向、优于原方程的百分比：`NOT RUN`；
- 问题三：三组两两交互效应、显著性、影响排序、最低损耗组合：`NOT RUN`；
- 问题四：附件三 400 个样本的损耗预测值、RMSE、MAE、泛化能力：`NOT RUN`；
- 问题五：最优温度、频率、波形、磁通密度峰值、材料及目标值：`NOT RUN`；
- 任何来自旧 run、未登记文件、手工复制表格或无 artifact 路径/SHA256 的数字：不得引用。

## 写作前强制核对规则

1. 每个数字必须指向一个当前 run 的 artifact 和一个 evidence_id；
2. 实验数字必须同时指向 `run_id` 和 `experiment_id`；
3. 论文只能使用 `evidence/active-evidence-set.yaml` 选中的当前版本；
4. 预测集无标签时，必须写“预测值”，不能写“测试准确率”；
5. 任何未运行的系数、误差、最优解或图表统一标记为 `NOT RUN`，不得用示例数字替代。

## 当前验证状态

- `EXP-Q1-BASELINE-001`：失败运行，不能提供数字证据；
- `EXP-Q1-BASELINE-002`：OBSERVED，证据完整；
- `EXP-Q1-MODEL-COMP-003`：OBSERVED，证据完整且已被 Active Evidence Set 选中；
- Q2、Q3、Q4、Q5：没有 OBSERVED 实验记录，不能写入任何实验数字。
