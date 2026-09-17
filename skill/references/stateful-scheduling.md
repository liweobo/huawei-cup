# Stateful Scheduling

## Purpose

当优化问题的可行性取决于随动作变化的系统状态时，用一个轻量 Contract 约束正式搜索。此文件只定义通用接口与 gate，不规定具体算法或行业参数。

## Activation

满足任一条件时检查是否为 `STATEFUL_SCHEDULING`：

- 决策是否可执行取决于此前动作；
- 机器、车辆、工件、队列、buffer 或位置随时间变化；
- 动作改变以后动作的合法性；
- 存在 blocking、queue、finite buffer 或动态资源占用；
- 存在 setup、travel、processing、release 或 precedence 状态；
- 仅凭最终排列无法判断完整可行性。

不要因为题目出现“调度”二字自动激活。只有 feasibility depends on evolving system state 时激活。

## Contract

正式 Improved / Primary search 前建立：

```yaml
stateful_scheduling:
  problem_type: STATEFUL_SCHEDULING
  state_variables: []
  resources: []
  queues_or_buffers: []
  time_representation: ""
  terminal_condition: ""
  legal_action_definition: ""
  transition_definition: ""
  hard_invariants: []
  objective_definition: ""
  candidate_representation: STATE_COUPLED
  search_mode: ""
  decoder_required: false
  feasibility_mode: BY_CONSTRUCTION
  status: PASS
```

`candidate_representation`：

- `STATE_COUPLED`：candidate 由真实 state、legal action 和 transition 产生；
- `SEQUENCE_WITH_FEASIBLE_DECODER`：序列由明确 decoder 转成真实 schedule；
- `SEQUENCE_ONLY`：只有抽象排列，没有能保证或验证实际状态转移的 decoder；
- `OTHER`：需要额外说明。

`feasibility_mode`：

- `BY_CONSTRUCTION`：所有扩展都通过 legal-action 和 invariant gate；
- `DECODE_AND_VERIFY`：decoder 生成真实 schedule 并显式验证硬约束；
- `POST_HOC_ONLY`：只提出候选后在末端检查，不能作为正式 Improved / Primary search。

状态只需足以判断四件事：当前合法动作、动作后的 next state、hard invariant 是否保持、是否 terminal。题目自行实例化字段，不要求固定使用所有示例字段。

## Search Gate

如果 `problem_type = STATEFUL_SCHEDULING`、`candidate_representation = SEQUENCE_ONLY` 且没有可保证/验证真实状态转移的 decoder，状态为 `STATE_SEARCH_UNVERIFIED`，不得把该候选标为正式 Improved / Primary。

硬约束非法 action 不应进入搜索；不能仅用大 penalty 维持形式上的可扩展性，除非题目明确允许软违约。`transition(state, action)` 必须更新真实资源、队列、容量、位置、时间与完成状态，并保持 hard invariants。transition 后违反硬约束即为 invalid，不得继续扩展。

## Decoder Exception

Permutation 或 sequence-based scheduling 可以合法使用，但必须满足：

1. 使用明确定义的 feasible decoder 生成真实 schedule；
2. decoder 显式处理全部 hard constraints；
3. objective 在 decoded schedule 上计算；
4. infeasible decode 不参与 incumbent selection。

抽象 permutation score 不能直接选最终方案。

## Objective And Incumbent

正式 objective 必须来自 realized 或 decoded feasible schedule。surrogate 只能用于 search priority / heuristic guidance，并标为 `SURROGATE`；不能用 surrogate score 击败真实可行候选。

候选至少记录：

```yaml
candidate_id: ""
feasible: true
objective: 0
objective_components: {}
runtime: 0
termination_reason: ""
provenance: ""
```

只有 `feasible = true` 才参与 incumbent selection。maximize 取最大真实 objective，minimize 取最小；多目标沿题目定义的 priority / weight / Pareto protocol。termination 时仍有未调度对象，不能标为 terminal feasible solution。

## Final Audit

search 与 simulator 共用 legal actions、transition 和 invariant checks 只解决“搜索不要浪费在非法状态空间”。正式 output 仍必须经过独立 feasibility audit，重新检查 hard constraints、整数性、容量、唯一性和业务输出。

heuristic、beam、greedy 或 local search 的最好结果只能称 `BEST FOUND`；没有 exact proof 或 valid bound 时不得称全局最优。

## Helper

需要轻量 gate 或 incumbent 校验时使用 [`stateful_scheduling.py`](../scripts/stateful_scheduling.py)。它只提供 Contract 校验、动作可扩展性和 feasible incumbent 选择，不包含通用仿真平台或具体算法。

## Reviewer Codes

- `STATE_FEASIBILITY_DECOUPLED`：先优化理想排列，动态状态决定可行性却没有合法 decoder；
- `HARD_CONSTRAINT_AS_PENALTY`：硬约束非法动作只被大 penalty 处理；
- `SURROGATE_OBJECTIVE_AS_FINAL`：候选排列 surrogate 得分被当作最终真实 objective。
