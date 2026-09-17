# Stateful Scheduling Readiness

## Scope

This change adds only a stateful scheduling search contract. It does not add
a generic simulator, MILP DSL, CP-SAT wrapper, GA framework, routing solver,
or fourth historical problem.

## Files

Skill:

- `skill/references/stateful-scheduling.md`
- `skill/scripts/stateful_scheduling.py`
- `skill/references/models/optimization.md`
- `skill/references/models/index.md`
- `skill/references/model-selection.md`
- `skill/rules/modeling.md`
- `skill/workflows/design-model.md`
- `skill/workflows/run-experiment.md`
- `skill/workflows/validate-model.md`
- `skill/workflows/reviewer.md`

Tests:

- `development/tests/test_stateful_scheduling.py`
- `development/tests/test_skill_self_contained.py`

2022C post-fix regression:

- `development/benchmarks/runs/historical_2022_c_buffer_scheduling/run-003-postfix/`

## Contract Gate

The new gate distinguishes:

- `STATE_COUPLED` with `BY_CONSTRUCTION`;
- `SEQUENCE_WITH_FEASIBLE_DECODER` with `DECODE_AND_VERIFY`;
- `SEQUENCE_ONLY` without a decoder, which remains `STATE_SEARCH_UNVERIFIED`;
- `POST_HOC_ONLY`, which cannot be formal Improved / Primary search.

Hard-invalid actions are rejected before expansion. A transition that breaks
an invariant cannot become a next state. Feasible incumbent selection uses
only realized/decoded objective, never a surrogate.

## Generic Regression

`development/tests/test_stateful_scheduling.py` covers A-L:

- stateful detection for dynamic buffer/machine;
- non-activation for static allocation;
- sequence-only rejection;
- feasible-decoder acceptance;
- illegal busy-machine action;
- buffer overflow;
- precedence;
- hard rule not treated as penalty;
- feasible incumbent selection;
- surrogate versus realized objective;
- terminal completeness;
- independent final audit requirement;
- legal action decoder checks;
- Reviewer error codes.

## 2022C Post-Fix Regression

The regression reuses the frozen run-002 inputs and complete event loop. The
state-coupled candidate enumerates legal PBS actions in the current state and
exports `result31.xlsx` / `result32.xlsx`; independent audit reports zero hard
violations.

The new candidate does not improve the objective in this iteration:

| scenario | old | new state-coupled |
|---|---:|---:|
| Q1 | 53.367 | 51.801 |
| Q2 | 53.643 | 53.058 |

This is expected to be possible. Contract readiness is about search validity
and state coupling; it is not a claim of better solution quality.

## Historical Integrity

- `historical_2022_c_buffer_scheduling/run-002` is not modified.
- 2024C frozen assets are not modified.
- 2023E frozen/reference assets are not modified.
- No 2022C excellent solution or answer was accessed.
