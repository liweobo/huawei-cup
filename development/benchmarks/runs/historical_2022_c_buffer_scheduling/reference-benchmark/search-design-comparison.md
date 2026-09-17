# Search Design Comparison

## Current Skill

### Run-002

- Baseline: source-order.
- Improved candidates: lane-choice greedy and a bounded abstract
  target-sequence adjacent-swap experiment.
- Failure mode: the abstract candidate is scored before its physical
  realization and does not improve the realized weighted objective.

### Run-003 Post-Fix

- Representation: `STATE_COUPLED`.
- Legal-action gate: current PBS state.
- Transition: complete frozen event loop.
- Search: deterministic one-step priority.
- Result: feasible and independently audited, but O1 remains zero.

## Reference Patterns

| pattern | references with evidence | meaning for the current Skill |
|---|---|---|
| constructive greedy initial solution | R-02, R-04 | The Skill has this. |
| feasible schedule decoder / simulator | R-01, R-03, R-04, R-06, R-07 | Legal alternate representation; the Skill supports the decoder exception. |
| return decision as a searchable action | R-01, R-02, R-03, R-04, R-05 | Current search has the action but no structured policy for when returning improves the objective. |
| neighborhood improvement after construction | R-02, R-04, R-05, R-06 | Current run-003 has no improvement phase beyond one-step choices. |
| multi-step or population search | R-01, R-02, R-03, R-04, R-05, R-06 | The algorithm name varies; the common modeling fact is that one-step greedy is not enough. |
| lane/return/sequence action design | virtually all references | The current Skill lacks a general principle for defining domain-valid moves. |

## Candidate Generalizations

### G1-A: Feasibility-Preserving Improvement

Construct a feasible solution, then apply only feasible moves (swap,
insertion, block move, return/re-route) and compare the realized objective.
This is supported by R-02 and R-04 and is independent of automotive PBS.

### G1-B: Search Horizon / Lookahead

Choose actions by evaluating future state consequences, not only the
immediate score. This is supported by the multi-step/iterated methods in
R-01, R-02, R-03, R-04 and R-05. It is generalizable to scheduling and
resource allocation, but its implementation can be expensive.

### G1-C: Structure-Aware Neighborhood Design

Define moves from the problem's actual action grammar: lane assignment,
return/no-return, sequence insertion, block move, dispatch choice. This is
the broadest and most reference-supported candidate.

## Why The Algorithm Name Is Not The Gap

The references use GA, SA, grey wolf, greedy, dynamic programming and
Markov decision processes. The common denominator is not one algorithm.
It is a **domain-valid move set** plus repeated evaluation of a feasible
realized schedule. A recommendation to add GA/SA/CP-SAT would be
problem-specific and over-engineering.
