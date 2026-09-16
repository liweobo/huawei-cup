# 有验证依据的特征集设计与增量消融

仅在多源、多阶段、高维输入，或声称某类信息带来增益时加载。设计信息组
（FEATURE SET DESIGN）与在某个集合中学习变量筛选（FEATURE SELECTION）是两件事。
不是默认增加模型、PCA 或搜索所有变量组合。

## Feature Set Contract

在训练之前声明并存入 Experiment Record 的 `feature_set_contract`：

```yaml
task:
prediction_setting:
unit_of_analysis:
target:
feature_groups:
  - name:
    description:
    source:
    columns_or_builder:
      columns: [] # 必须解析为具体列，供实际 X 核对
      derived: false
      # 派生组另填 inputs、formula（或可追踪 builder）、units
    availability: VERIFIED # 未确认的组不能进入正式预测
    temporal_role:
    entity_level:
    dimension:
    domain_rationale:
    required_or_optional:
baseline_feature_groups: []
candidate_incremental_groups: []
required_groups: []
optional_groups: []
excluded_groups: []
exclusion_reason: {}
temporal_scope: {} # status + 正式时间合同/边界；静态不适用要说明理由
group_scope: {} # status、independence_required；与正式实体合同一致
selection_method: NONE
selection_scope: NONE # TRAIN_FOLD / INNER_VALIDATION（有数据驱动筛选时）
comparison_protocol:
  planned_candidates: []
  design_source: PROBLEM_STRUCTURE
  search_strategy: PLANNED_SMALL
  selection_validation: FIXED_CV # 扩大数据驱动搜索需独立/nested validation
  rationale:
status: PASS
```

按来源、语义、时间、模态或建模角色形成可解释的组，例如初始状态、几何、频域、
历史行为、环境、运行条件、随访摘要。不要为凑消融表把每列任意命名成一个组。
分组可来自题目表结构或物理意义，在 CV 外声明；若按全数据 target 相关性留组，
就属于需要内部验证的数据驱动选择。各派生组记录输入、公式/代码、单位、可用时点
与理由，可用 difference、ratio、rate、slope、summary 等少量有依据表示。

## 保留 baseline，再受控改变信息

Setting B = A + 新信息时，先保留 A 的全部合法 baseline。移除列/组必须逐项记录
`REMOVED_FROM_BASELINE` 和 `removal_reason`；合法性审计发现的非法或未知时点字段也要
明确排除，不能以“保留 baseline”为由继续使用。`X` 与 `部分 X + Y` 的差值不能解释
为 Y 的增量价值，即使删除有理由也不行。

预先设计少量有问题语义的顺序：B → B+G1 → B+G1+G2；必要时比较 Full 与 Full−G1、
Full−G2。不要做默认 2^N 搜索、跑几十组挑最高 CV 分，或看到结果后不断加组合。
大规模选择必须有独立/嵌套评价，否则报告 `FEATURE_SET_SEARCH_OVERFIT_RISK`。

所有比较固定同一 eligible sample IDs、target/定义、cutoff、fold IDs、seeds、模型族、
超参数政策、预处理政策和指标定义。学习的列筛选可随训练 fold 改变，**政策**保持一致。
不同缺失模式导致的 100 vs 72 样本不能归因于特征：先在共同样本上重跑双方的受控比较，
再另报 coverage trade-off，区分 PERFORMANCE CHANGE 与 SAMPLE COMPOSITION CHANGE。
允许训练内插补保持人群；不能为每种特征方案另抽一组 folds。

## Validation 与 provenance

所有 learned steps（variance/correlation/MI/LASSO/RFE/model selection、PCA、scaling、
clustering、embeddings、trajectory prototypes）必须只 fit 当前训练 fold，validation
仅 apply/transform。Target-blind 仍会泄漏；固定无学习公式可以在外层按实体计算，
但先通过 Temporal Gate、**filter before aggregation**，再审计实体依赖。
重复实体使用同一合法 group split。Ordinal 保留 MAE/RMSE/QWK/Within-One-Level；
不平衡分类保留概率与少数类指标，禁止只按 Accuracy 排名。

在原 Experiment Record 上按需增补 `feature_set`，不要替换原 provenance：

```yaml
feature_set_id:
feature_groups: []
feature_columns: [] # 实际喂给 pipeline 的列
baseline_feature_set:
incremental_groups: []
removed_groups: []
removals: [] # {column, status: REMOVED_FROM_BASELINE, removal_reason}
selection_method:
selection_scope:
sample_ids: [] # 唯一行 ID，顺序与 target_values、entity_ids 对齐
entity_ids: [] # 重复实体保留真实映射，不冒充新的独立实体
fold_ids: [] # {fold_id, train_ids, validation_ids}，直接保存实际成员
model_family:
comparison_parent:
comparison_reason:
protocol: {} # target、target_definition、target_values、temporal_cutoff、random_seeds、
             # model_family、hyperparameter_policy、preprocessing_policy、metric_definitions、
             # primary_metric、target_type；不平衡时 imbalanced: true
fit_log: [] # {fold_id, operation, scope: TRAIN_FOLD, fit_ids}，真实 fit 输入
```

用 [`feature_sets.py`](../scripts/feature_sets.py) 的 `feature_set_errors()` /
`apply_feature_set_gate()` 审核；`runtime_provenance.validate_experiment_record()` 对
声明 `feature_set_comparison` 的 protocol 自动要求该扩展。实际 train/valid IDs、
group gate、temporal gate 独立保留。日志不能替代运行代码复核。
`audit_feature_comparison(parent, candidate, contrast=...)` 在运行前检查协议；
失败的比较不能成为信息增益证据。`composition_diagnostic` 只描述混合输入变化。

## Paired evidence 与负结果

按同一 fold 计算 `delta_i = metric(candidate)_i − metric(parent)_i`，报告逐 fold 分布、
均值、标准差、mean/median delta 和 sign consistency。QWK/AUC/PR-AUC 越高越好；
MAE/RMSE 越低越好。`paired_metric_summary()` 显式接收方向和**事前** practical_delta；
drop 对照以删组后的退化表示该组贡献。其保守描述标签要求 mean benefit 大于预设阈值
和 delta 标准差、median>0 且方向一致率达预设值；这不是显著性检验、独立重复或 CI，
不得事后降低门槛。结果仍需按目标、相关指标和实际成本解释。

单 fold +0.01 不证明改善。小且不稳定的差异保存为 `NO_CLEAR_INCREMENTAL_VALUE`
（论文可写 NO CLEAR INCREMENTAL BENEFIT）；无支持组可记 `FEATURE_GROUP_NOT_SUPPORTED`。
保留负结果，不宣称“已经证明完全无效”。检查每个训练 fold 的维度/样本比、缺失、
计算与解释成本；几乎无收益时可保留简单方案。重新评估 regularization 或 fold-safe
selection 的必要性，不因高维自动 PCA。最终逐组解释来自哪里、为何可用/保留、
何时可得、是否派生/选择。

## Reviewer / Paper Claim

- baseline 或 samples/folds/model 同时改变却宣称新增组增益：`UNCONTROLLED_FEATURE_SET_COMPARISON`。
- 全数据筛选或 target-blind learned transform → CV：`FEATURE_SELECTION_LEAKAGE`。
- 无预先依据的大组合挑最好：`FEATURE_SET_SEARCH_OVERFIT_RISK`。
- 缺来源、时点或构造：`FEATURE_PROVENANCE_INCOMPLETE`。

用 `review_feature_claim()` 检查上述记录；Paper Claim 可附 `feature_set_evidence`
（candidate/parent 完整记录、contrast、paired_evidence）接入原论文 validator。
必须引用当前 run 的受控实验才能写“该信息提升性能”；否则只能写“模型使用该信息”。
即使同 CV 下比较通过，选中方案的泛化收益仍需独立新数据检验，不能把选模后的 CV
最高值当作无偏最终性能。
