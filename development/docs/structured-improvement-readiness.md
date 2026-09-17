# Feasibility-Preserving Structured Improvement Readiness

## Capability

`structured-improvement.md` defines a lightweight contract for improving a
feasible incumbent when no exact optimum is available:

```text
feasible incumbent
-> decision-structure move family
-> real realization / decoder
-> hard feasibility gate
-> realized objective
-> monotone incumbent update
-> bounded stopping rule
```

The helper `skill/scripts/structured_improvement.py` only validates
contracts, compares MAX/MIN objectives, updates feasible incumbents, tracks
budgets and validates traces. It does not implement GA, SA, PSO, beam,
routing or a solver platform.

## Generic Tests

`development/tests/test_structured_improvement.py` covers A-L:

- known objective improvement;
- no-improvement negative result;
- infeasible move rejection;
- surrogate trap;
- working solution versus monotone incumbent;
- MAX and MIN directions;
- decoder integration;
- budget stop;
- deterministic reproducibility;
- move provenance;
- exact OPTIMUM exception;
- reviewer codes.

The synthetic known-improvement test verifies a genuine objective increase.

## 2022C Regression

`run-004-structured-improvement` uses the run-002 feasible schedule as the
initial incumbent and a bounded real adjacent-swap move family. Every
candidate is fully realized by the PBS event loop and evaluated with the
true weighted score.

Result:

| scenario | initial | final | evaluated | feasible | accepted | hard violations |
|---|---:|---:|---:|---:|---:|---:|
| Q1 | 53.367 | 53.367 | 24 | 24 | 0 | 0 |
| Q2 | 53.643 | 53.643 | 24 | 24 | 0 | 0 |

Status: `NO_REAL_INSTANCE_IMPROVEMENT`, which is an allowed negative
result. It is not rewritten as success.

## Final Status

```text
FEASIBILITY_PRESERVING_STRUCTURED_IMPROVEMENT_READY
generic_tests: PASS
synthetic_known_improvement: YES
structured_improvement_contract: PASS
2022c_regression: PASS
initial_incumbent_score: Q1=53.367, Q2=53.643
final_incumbent_score: Q1=53.367, Q2=53.643
objective_improved: NO
O1_before: Q1=0, Q2=0
O1_after: Q1=0, Q2=0
evaluated_moves: Q1=24, Q2=24
feasible_moves: Q1=24, Q2=24
accepted_moves: Q1=0, Q2=0
hard_violations: 0
stateful_scheduling_still_ready: YES
historical_assets_unchanged: YES
routes: 10 / unchanged
skill_only_self_contained: PASS
```
