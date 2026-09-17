# Modeling Rules

1. 模型选择必须来自目标、输入输出、约束、数据生成机制和验证条件，不从题目关键词直接推出算法。
2. 一个子问题可属于多个类型；先建立依赖图，再决定分阶段或联合建模。
3. 关键模型尽量有可运行 Baseline；若确实没有，必须解释比较基准是什么。
4. 假设必须参与变量、方程、约束或验证；无作用假设应删除。
5. 复杂度必须带来可测收益，例如误差、可行性、稳定性或解释能力改善。
6. 参数、边界和单位必须有来源或清晰估计方法；不可识别参数不能靠任意调参掩盖。
7. 优化结果必须检查约束、整数性、资源守恒和可执行性；启发式最好值不自动等于全局最优。
   若 feasibility depends on evolving system state，正式搜索必须通过 legal actions 和 transition 推进，或使用经验证的 feasible decoder；不能只在抽象排列上优化、最后再做 post-hoc 可行性检查。
   若已有 feasible incumbent 但无 exact proof，且离散决策改变可能改善真实 objective，应定义少量有 decision semantics 的 move families 做 structured improvement。候选须经过 hard feasibility 和 realized/decoded objective；working solution 可暂时变差，但 best feasible incumbent 必须单调。move、budget、stopping rule 和 search trace 必须可审计。
8. 不平衡二分类中 Accuracy 不得作为唯一或主要选模指标；必须比较多数类基线，并以少数类表现、类别平衡指标、概率质量和题目代价共同决策。
9. 非随机分配的 treatment / intervention / policy / action 先按 [Association Analysis Contract](../references/observational-association.md) 分析关联。高风险/高需求对象更可能接受措施，组间差异不能直接推出因果效应；没有独立识别依据不得声称 CAUSAL_EFFECT。
10. 普通 confounder 必须有处理前依据；响应、未来信息、处理后变量及未知相对时序的初始测量不能冒充处理前控制项。暴露时间未知标 EXPOSURE_TIME_UNVERIFIED；联合条件描述与因果/预测解释分别审查。
