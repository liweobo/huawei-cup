# Structured Improvement

## Purpose

当 optimization problem 已有合法 feasible incumbent，但没有 exact proof
证明其为最优，且改变少量离散决策可能改善真实 objective 时，定义一个小而
有明确 decision semantics 的 improvement phase。

本文件只定义 Contract、move provenance、feasibility gate、incumbent
规则、budget 和审计要求。它不规定 GA、SA、PSO、CP-SAT、MILP、beam 或任何
具体求解算法。

## Activation

同时满足以下条件时考虑 `STRUCTURED_IMPROVEMENT`：

1. 已有一个真正 feasible 的 incumbent；
2. exact method 没有给出有证明的 OPTIMAL；
3. solution quality 可能通过改变离散决策得到改善；
4. 可以定义少量 meaningful move families；
5. 每个 candidate 能通过真实状态、decoder 或 problem-specific
   realization 重新得到可行解。

不要因为题目出现“优化”或“调度”就自动激活，也不要为了追分制造无意义
local search。

## Contract

```yaml
structured_improvement:
  problem_type: ""
  objective_direction: MAXIMIZE
  incumbent_source: ""
  incumbent_feasible: true

  decision_structure: []

  move_families: []

  candidate_realization: ""
  feasibility_check: ""
  objective_evaluator: ""

  acceptance_rule: ""
  incumbent_update_rule: ""

  search_budget: ""
  stopping_rule: ""

  deterministic: true
  random_seed: null

  status: PASS
```

每个 move family 至少记录：

```yaml
name:
decision_component:
description:
rationale:
applicability:
expected_effect:
```

`decision_component` 必须指向题目真实决策结构，例如 sequence、assignment、
route、machine choice、optional action 或 dispatch policy。不能只写
`mutation()`、`random perturbation()`、`neighbor()` 或“随机改编码”。

## Move Design

Move families 应少量、结构化、有依据、可计算，并说明：

- 改变了哪个 decision component；
- 为什么可能影响 objective；
- 可能影响哪些 hard constraints；
- 如何重新得到真实可行解。

例如 swap、insertion、block move、assignment reassignment、route segment
modification、machine/resource reassignment、activate/deactivate optional
action、dispatch-policy change。通用原则不是枚举 move，而是要求 move 有
明确 decision semantics 和 rationale。

## Feasibility Integration

允许两种正式方式：

- `FEASIBILITY_BY_CONSTRUCTION`: move 本身只产生合法解；
- `MOVE -> FEASIBLE_DECODER / STATE_REPLAY -> VERIFY`: candidate 只有在
  hard feasibility gate 通过后才能进入真实 objective comparison。

非法 candidate 不能用巨大 penalty 伪装成有效 neighbor。与
[stateful-scheduling.md](stateful-scheduling.md) 的关系是：

- Stateful Scheduling 决定 candidate 是否被合法产生；
- Structured Improvement 决定在合法空间中如何继续改善。

二者可以串联，不互相替代。

## Objective And Incumbent

正式 improvement 只能比较 realized/decoded feasible solution 的真实
objective。surrogate 可以用作 neighbor ordering 或 search priority，
但不能更新 incumbent。

必须区分：

- `WORKING SOLUTION`: 可按 adaptation/acceptance rule 改变，允许临时变差；
- `BEST FEASIBLE INCUMBENT`: 只在真实 objective 改进时更新。

MAXIMIZE 时 best incumbent objective 不得下降；MINIMIZE 时不得上升。
如果题目是 weighted、lexicographic 或 Pareto objective，沿题目正式协议，
不得为了 local search 重设权重。

## Budget, Stop Rule And Reproducibility

必须显式记录至少一种停止规则：no improvement、max iterations、max
candidate evaluations、time budget、convergence 或 bounded neighborhood
exhaustion。比赛环境中还要限制总搜索预算，避免单个子问题吞掉全部时间。

至少记录：

```text
evaluated_moves
feasible_moves
accepted_moves
incumbent_updates
runtime
termination_reason
```

若搜索含随机性，记录 `random_seed`。若使用确定性搜索，记录
`deterministic: true`。多种子不是所有问题的强制要求。

没有改善是合法结果：允许 `NO_IMPROVING_MOVE_FOUND` 或
`NO_CLEAR_SOLUTION_QUALITY_GAIN`，不得为了证明 capability 而改变 objective。

## Search Trace

正式 trace 至少包含：

```yaml
iteration:
move_family:
candidate_id:
feasible:
objective:
incumbent_before:
incumbent_after:
accepted:
reason:
```

只保留足以审计、复现和解释的简洁信息，不保存巨型无价值 trace。

## Exact Optimality Exception

如果 exact solver 已给出 `OPTIMAL` 且存在有效 proof/bound，不要求再运行
heuristic structured improvement。该原则主要针对 heuristic、
constructive 或 partially solved 的组合优化任务。

找到更好解只能写 `BETTER FEASIBLE SOLUTION` 或 `BEST FOUND`，不能写
`GLOBAL OPTIMUM`，除非另有 exact evidence。

## Reviewer Codes

- `UNSTRUCTURED_OPTIMIZATION_SEARCH`: 重复随机生成完整解，却没有决策结构上的
  improvement design；
- `INFEASIBLE_NEIGHBOR_AS_VALID`: 非法 neighbor 只用 penalty 留在搜索中；
- `SURROGATE_IMPROVEMENT_CLAIM`: surrogate score 更新 incumbent；
- `IMPROVEMENT_EVIDENCE_MISSING`: 声称搜索提高结果，却没有
  baseline/incumbent 对比记录；
- `SEARCH_BUDGET_UNSPECIFIED`: 搜索完成但没有停止规则或预算。

## Helper

需要轻量 gate、方向比较、incumbent 更新、预算 bookkeeping 或 trace
校验时使用 [`structured_improvement.py`](../scripts/structured_improvement.py)。
它不实现 GA、SA、PSO、beam、routing solver 或完整搜索平台。
