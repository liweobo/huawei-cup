# 2022C Structured Improvement Regression

## Scope

This is a targeted, post-fix regression for
`FEASIBILITY_PRESERVING_STRUCTURED_IMPROVEMENT`. It reads run-002 and
run-003 but writes only under `run-004-structured-improvement`. It does not
modify any frozen run.

## Initial Incumbent

The initial feasible incumbent is the run-002 best-found schedule:

| scenario | weighted | O1 | O2 | O3 | O4 |
|---|---:|---:|---:|---:|---:|
| Q1 | 53.367 | 0 | 80 | 100 | 93.67 |
| Q2 | 53.643 | 0 | 81 | 100 | 93.43 |

## Improvement Contract

- `problem_type`: `STRUCTURED_IMPROVEMENT`
- objective direction: `MAXIMIZE`
- decision structure: vehicle sequence positions
- move family: `adjacent_swap`
- candidate realization: complete frozen PBS event loop
- feasibility check: real event-state hard invariants
- objective evaluator: `detailed_scores()` on the realized schedule
- acceptance: feasible candidate with greater weighted objective
- incumbent rule: monotone best-feasible objective
- budget: 24 candidate evaluations per scenario
- stopping rule: budget reached or no remaining move
- deterministic: true

## Run Result

| scenario | initial | final | evaluated | feasible | accepted | incumbent updates | hard violations |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q1 | 53.367 | 53.367 | 24 | 24 | 0 | 0 | 0 |
| Q2 | 53.643 | 53.643 | 24 | 24 | 0 | 0 | 0 |

The run completed all 24 bounded adjacent-swap candidates per scenario,
realized each candidate through the complete PBS event loop, and compared
the true realized objective. No candidate improved the incumbent:

```text
NO_REAL_INSTANCE_IMPROVEMENT
```

This is a legitimate negative result. It does not invalidate the
capability; the synthetic known-improvement regression proves that the
contract can accept an improving feasible move.

## Feasibility Audit

`audit-structured-results.py` independently reopened `result41.xlsx` and
`result42.xlsx` and reported zero code, position and receipt violations for
both files.

## Limitations

- The move family is deliberately small: adjacent swaps only.
- No claim is made that this is the best possible neighborhood or that the
  gap is resolved for all 2022C instances.
- No global optimum claim is made.
