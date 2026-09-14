# Evidence Rules

1. 所有核心结论必须能回溯到数据、代码输出、题面推导或已核验来源。
2. 未实际运行的数值标记 `NOT RUN`；无法确认的事实标记 `[需要验证]`。
3. 外部数据、代码、参数和文献使用 `templates/source-record.md` 记录来源、访问日期、用途和核验状态。
4. 不得编造文献、引用、数据、实验结果、图表、最优解或预测值。
5. 摘要、正文、表格、图和代码中的数字、单位、变量与数据版本必须一致。
6. 观察到的相关关系不得无额外识别依据就写成因果结论。
7. 数据审计数字必须来自 Canonical Data Audit Summary；同一 response 中
   对同一 canonical metric 的矛盾值属于 consistency failure。
8. 模拟扰动、重采样或敏感性分析必须标记为 `SIMULATED_PERTURBATION`，
   不得写成 NEW_MEASUREMENT 或 REAL_WORLD_REPEATED_EXPERIMENT。
9. `CODE_RUN`、`EXPERIMENT_RESULT`、`VALIDATION_RESULT` 和 `PAPER_CLAIM` 必须绑定 `run_id`；实验类证据同时绑定 `experiment_id`。
10. 论文只消费 [`../templates/active-evidence-set.yaml`](../templates/active-evidence-set.yaml) 选中的当前证据版本。跨 run 引用必须显式标记 `historical_evidence_reference`，否则属于 `STALE_EVIDENCE_REFERENCE`。
11. Paper Claim 使用 [`../templates/paper-claim.yaml`](../templates/paper-claim.yaml) 记录 artifact 和 JSON path；“确实运行过”不能替代版本选择。
12. Evidence Ledger、Experiment Record、Paper Claim、Reviewer Report 和 Final Check 引用的 artifact 必须在当前 run archive 或 canonical source 中存在，并能通过路径和 SHA256 核验。
13. 未登记文件分类为 `ORPHAN` 并报告，不得因为文件名、mtime 或目录大小直接删除。
