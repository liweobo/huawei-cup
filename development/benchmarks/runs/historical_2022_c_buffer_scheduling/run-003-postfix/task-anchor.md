# Task Anchor: 2022C State-Coupled Post-Fix Regression

- **Goal**: Validate the new stateful scheduling contract on the frozen
  2022C PBS problem without modifying the blind-run artifacts.
- **Benchmark ID**: `historical_2022_c_buffer_scheduling`
- **Run ID**: `historical_2022_c_buffer_scheduling/run-003-postfix`
- **Boundary**: read run-002 code/inputs/results; write only this run.
- **Required comparison**:
  - run-002 formal feasible best-found incumbent;
  - run-003 `STATE_COUPLED` formal candidate.
- **Done When**:
  - candidate search expands only legal actions on the real PBS state;
  - every formal candidate has a real simulated objective;
  - infeasible candidates are excluded from incumbent selection;
  - result is independently audited with zero hard violations;
  - generic A-L tests, full regression, and skill-only self-contained tests pass.

## Current Regression Status

The first custom state-coupled runner produced a misleading in-memory score
before terminal completion was reconciled. Its exported workbooks failed the
independent audit and are `INVALIDATED`. They must not be used as the formal
post-fix candidate. The contract-level implementation and generic tests
remain valid; the 2022C targeted regression is being reworked to use the
same complete frozen event loop rather than a partial copied loop.
