# 2022C Third-Problem Blind Run

## 1. Source Provenance

- Source directory:
  `https://github.com/zhanwen/MathModel/tree/master/国赛试题/2022年研究生数学建模竞赛试题/C`
- Status: `ACCEPTED` historical mirror; no independent official-host claim.
- Raw files and SHA256:
  - problem `.docx`: `157226574e34a5a02fc805ff1c0db400a2e28aa3c40c63a75582fd27f83e7c55`
  - `附件1.xlsx`: `6e972f0a62f61e88bec60d36d2f63c79060d88146ce3844198ea7c32cad93459`
  - `附件2.xlsx`: `e379230b44ec24fff254515d1ddcf1489fdc6adc596c03434212ea015521460b`
  - `附件3.xlsx`: `44b2f6d99ef57f1792fc7205716c1bcdf49d183dbd5e014bc5bb01e19a63eb37`
  - `附件4.xlsx`: `adaca8aeeb3bf85b8928506d511cb691d1717d9ad3451a0756116a052c600679`
- Original files remain in `run-001/raw`; run-002 uses verified ASCII
  mirrors in `inputs-raw/`. No excellent-solution, answer, solution writeup,
  or third-party 2022 C code was accessed.

## 2. Problem Facts

The full traceable statement extraction is in `problem-facts.md`. The main
facts are:

- six inbound FIFO lanes with 10 positions each;
- one return lane with 10 positions;
- one receiving transfer machine and one delivery transfer machine;
- 9-second lane movement;
- receiving/delivery times `[18,12,6,0,12,18]`;
- inbound-to-return times `[24,18,12,6,12,18]`;
- return-to-inbound times `[24,18,12,6,12,18]`;
- Q1 keeps all stated rules; Q2 removes only the return-position priority and
  first-position-one-arrival priority rules;
- four weighted score components with weights `0.4, 0.3, 0.2, 0.1`.

The adopted interpretation of zero-time load/unload overlap and immediate
lane movement is documented as `AMBIGUOUS` / adopted in `problem-facts.md`.

## 3. Data Audit

All four workbooks were actually read with `openpyxl`.

| file | sheet | data shape | missing | duplicate rows |
|---|---|---:|---:|---:|
| attachment1.xlsx | Sheet1 | 318 x 4 | 0 | 0 |
| attachment2.xlsx | Sheet1 | 318 x 4 | 0 | 0 |
| attachment3.xlsx | Sheet1 | 74 x 2 | 0 | 0 |
| attachment4.xlsx | Sheet1 | 50 x 100 template | 0 | 0 |

Attachment 3 contains 60 inbound codes, 10 return codes and fixed codes
`0,1,2,3`. Attachment 4 is a blank template. Full details are in
`data-audit-summary.md` and `work/data-audit.json`.

## 4. Subproblem Decomposition

- **Q1-A1 / Q1-A2**: full-rule PBS scheduling for Attachment 1 and 2.
- **Q2-A1 / Q2-A2**: same scheduling problem after removing only the two
  stated priority constraints.
- Required outputs: `result11.xlsx`, `result12.xlsx`, `result21.xlsx`,
  `result22.xlsx`.

## 5. Mathematical Formulation

The explicit sets, parameters, binary/integer variables, objective and hard
constraints are in `mathematical-model.md`. The key variables distinguish
inbound-lane occupancy, return-lane occupancy, transfer-machine action starts,
and final-assembly arrival order. The model does not convert hard PBS rules
into penalties.

## 6. Decision Variables

- `x[i,l,p,t]`: inbound occupancy;
- `r[i,p,t]`: return-lane occupancy;
- `z[i,t]`: transfer-machine occupancy;
- `y[i,t]`: final-assembly receipt;
- `a,b,c,u[i,l,t]`: receive, assembly, return and return-to-lane actions;
- `o_t`: final arrival order.

## 7. Objective Functions

The four components are computed exactly from the final sequence and
completion time:

```text
O1 = 100 - number of consecutive hybrid gaps not equal to 2
O2 = 100 - number of non-1:1 drive blocks
O3 = 100 - return-lane use count
O4 = 100 - 0.01 * max(0, T - (9C + 72))
Weighted score = 0.4*O1 + 0.3*O2 + 0.2*O3 + 0.1*O4
```

No arbitrary weights were introduced; all four weights come directly from
the statement.

## 8. Constraints

The implemented hard-constraint families are:

1. source-order consumption at the paint exit;
2. one vehicle per inbound and return position;
3. FIFO direction and immediate downstream movement;
4. one payload and no interruption per transfer machine;
5. carrier return to the central home position before the next action;
6. return-position-10 priority in Q1;
7. first-arrival priority at inbound position 1 in Q1;
8. no delivery machine idle while a position-1 body exists;
9. no direct return-lane-to-assembly move.

Each constraint family is independently checked in
`work/feasibility-audit.json`.

## 9. Baseline

The simplest legal baseline is `source-order`: receive source vehicles,
advance FIFO lanes, and deliver without using the return lane. It is a real
run, not a placeholder.

Full-instance results:

| scenario | feasible | hard violations | weighted score |
|---|---:|---:|---:|
| Q1 attachment 1 | true | 0 | 53.367 |
| Q1 attachment 2 | true | 0 | 53.367 |
| Q2 attachment 1 | true | 0 | 53.643 |
| Q2 attachment 2 | true | 0 | 53.643 |

The baseline is feasible but weak: O1 is 0 on the full data.

## 10. Solver / Algorithm

- Algorithm: deterministic discrete-event scheduler with source-order,
  score-aware greedy, and a bounded target-sequence adjacent-swap experiment.
- Solver: no external MILP/CP solver; Python 3.12.10 / NumPy 2.5.2 /
  OpenPyXL 3.1.5.
- Random seed: none.
- Time limit: none.
- Runtime: complete 8-scenario run approximately 82 seconds in the first
  full execution; selected formal outputs were regenerated after state-model
  fixes.
- Termination: finite simulation completion.
- Provenance: `work/solver-provenance.json` and each candidate's
  `solver-log.json`.

## 11. Real Results

Selected formal results (highest feasible score under the same problem
definition):

| output | source | completion time | return uses | O1 | O2 | O3 | O4 | weighted |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| result11.xlsx | Q1/A1 source-order | 3567 | 0 | 0 | 80 | 100 | 93.67 | 53.367 |
| result12.xlsx | Q1/A2 source-order | 3567 | 0 | 0 | 80 | 100 | 93.67 | 53.367 |
| result21.xlsx | Q2/A1 source-order | 3591 | 0 | 0 | 81 | 100 | 93.43 | 53.643 |
| result22.xlsx | Q2/A2 source-order | 3591 | 0 | 0 | 81 | 100 | 93.43 | 53.643 |

The four result workbooks use the required vehicle-row / second-column
layout. They are not global optima.

## 12. Feasibility Audit

`code/audit_results.py` re-opened each final workbook and checked:

- matrix dimensions and consecutive time index;
- allowed region codes from Attachment 3;
- one vehicle per lane/return position per second;
- vehicle-row uniqueness and initial placement;
- final-assembly receipt;
- completion-time consistency.

All four formal workbooks have `0` hard violations and `FEASIBLE` status.
The audit is independent of the simulator's own `feasible` flag.

## 13. Optimality / Solution-Quality Evidence

No exact global-optimum claim is made. The full 318-vehicle discrete
multi-machine problem was not solved to proven optimality. The selected
solutions are `BEST FOUND / HEURISTIC`. Their quality limitation is visible:
objective 1 remains zero, and no solution uses the return lane.

The small-instance check enumerated all 6 permutations of a 3-vehicle
synthetic instance and verified the score functions, but this is only a
score/implementation check, not a full-instance bound.

## 14. Subproblem Completion

- Q1 Attachment 1: COMPLETE, feasible result generated.
- Q1 Attachment 2: COMPLETE, feasible result generated.
- Q2 Attachment 1: COMPLETE, feasible result generated.
- Q2 Attachment 2: COMPLETE, feasible result generated.

Quality is weak; completion is not the same as optimization quality.

## 15. Skill Strengths

- It correctly forced a statement-first model before algorithm choice.
- It preserved the raw files and recorded hashes.
- It provided an explicit constraint trace and a feasible baseline.
- It prevented a heuristic best-found result from being called global
  optimum.
- It required a run-scoped workspace and independent feasibility evidence.

## 16. Skill Weaknesses

- The optimization reference is too generic for a stateful discrete-event
  scheduling problem: it names MILP/GA/SA but does not require an event-state
  abstraction before heuristic design.
- It does not have a reusable incumbent/selection rule for multiple
  heuristic candidates.
- It does not explicitly force return-lane closure or action-level
  feasibility in a scheduling candidate.
- It treats optimization validation as a generic constraint checklist,
  which led to several implementation discoveries only during independent
  result auditing.

## 17. First Meaningful Failure

**FIRST_MEANINGFUL_FAILURE: stateful optimization search decoupled from
discrete-event feasibility.**

The score-aware target-sequence experiment optimized an abstract permutation
and then checked whether the PBS could realize it. The resulting sequence
did not materially improve the real schedule, while the feasible source-order
policy remained best-found. The required next modeling move is to make the
search state and the PBS event state the same object, not to add another
generic metaheuristic.

The earlier implementation bugs found during the run were fixed inside the
run's own code and are not counted as Skill defects.

## 18. Failure Classification

**P1 GENERALIZABLE OPTIMIZATION GAP.**

It does not invalidate the four feasible results, but it clearly reduces
competition quality because the method cannot improve the dominant stated
objective on the real instances.

## 19. Generalizable Gap Candidate

**TOP 1 GAP: stateful scheduling search contract.**

For optimization subproblems whose feasibility is defined by a
discrete-event state machine, the Skill should require the candidate
representation to include the actual resource state (machines, queues,
buffer positions, release times) and require every search move to be
replayed through that state machine before objective evaluation.

## 20. Remaining Uncertainty

- The zero-time load/unload overlap interpretation is not unique.
- The "block starts with 2 or 4" objective 2 edge case has an adopted
  interpretation.
- No lower bound or full-instance optimum is available.
- The best-known result is feasible but mathematically weak for O1.

## 21. Historical Integrity

- Historical 2024C and 2023E areas were not modified.
- No excellent-solution or answer source was opened.
- `skill/` Git tree before: `7ab25e144b214969f987df18d8357eb210f2b35d`.
- `skill/` Git tree after: `7ab25e144b214969f987df18d8357eb210f2b35d`.
- `git diff -- skill` is empty.
- Existing regression suite: `251 passed` in `118.82s`.

## 22. Final Decision

**B. GENERALIZABLE_OPTIMIZATION_GAP_FOUND**

The blind run produced valid, independently audited feasible outputs, but
exposed a single clear generalizable optimization-modeling gap: stateful
search must be coupled to discrete-event feasibility before heuristic
selection. Do not modify `skill/` in this run; await human review.

## Completion Status

```text
THIRD_PROBLEM_BLIND_RUN_COMPLETE

problem:
2022C 汽车制造公司涂装-总装缓存区调序调度优化问题

skill_modified:
false

excellent_solutions_accessed:
false

subproblems_completed:
4 / 4 (Q1 and Q2 on Attachments 1 and 2; feasible real schedules)

final_solution_feasible:
YES

optimality_claim:
BEST FOUND / HEURISTIC FEASIBLE SOLUTION; no global optimum claimed

first_meaningful_failure:
stateful optimization search decoupled from discrete-event feasibility

failure_level:
P1

generalizable_gap_candidate:
stateful scheduling search contract

recommended_next_action:
Await human review of the P1 stateful scheduling-search gap before changing
any Skill file.
```
