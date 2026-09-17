# Task Anchor: 2022C Structured Improvement Regression

- **Goal**: Validate feasibility-preserving structured improvement on the
  frozen 2022C PBS benchmark.
- **Run ID**: `historical_2022_c_buffer_scheduling/run-004-structured-improvement`.
- **Boundary**: read run-002/run-003 and reference-benchmark; write only
  this new run. Do not modify any prior run.
- **Initial incumbent**: run-002 feasible best-found (Q1 `53.367`,
  Q2 `53.643`).
- **Required move provenance**: real decision component, rationale,
  realization, feasibility check and real objective evaluator.
- **Done When**:
  - a bounded feasible move search actually runs;
  - every candidate is decoded/realized before comparison;
  - infeasible candidates are rejected before incumbent comparison;
  - working solution and best incumbent are separated;
  - trace and budget are recorded;
  - final candidate has zero hard violations under independent audit.
