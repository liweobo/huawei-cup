# Validation

## Source And Static Network

Original SHA256 checks pass, XLS readers agree, column-origin convention has
an explicit source witness and source-cell CSV traceability. Park blanks,
diagonal OD and index11.54 are retained without imputation/clipping.
Independent static audits pass for baseline, consolidated and final designs.
The final commodity conservation residual is1.0914e-11t/day and independent
objective reconstruction differs by7.45e-8yuan/day. All110 centres meet3km
coverage and all demanded endpoint pairs are reachable in the nominal design.

## Operations And Phases

Both deterministic queue policies have independently valid train payloads,
headway, dispatch spacing, route precedence and freight accounting, but fail
terminal full clearing. Closure=SCENARIO_ASSUMED, not full physical validation.
Event propagation has no time-step truncation;1080minutes is the given operating
horizon and all pending freight is accounted at the boundary.
Independent yearly audit passes equal-work reconstruction, endpoint
commissioning, active-primary connectivity and retained-route static capacity
with explicit surface fallback. This is not full-year service feasibility.
All eight full targets fail, and no30-year expansion design is certified.

## Small Oracles

Four newly written network tests and two six-node queue tests pass. These verify
relevant graph/flow/cost/removal and exact arrival/transfer precedence cases.
They are implementation tests only, not substitutes for original-data results.
No run-001 oracle was reused.

## Regression Results

| Check | Result |
|---|---|
| Byte-identical isolated development/tests | 304 PASS,1 FAIL (enclosing-run path guard) |
| Local network and queue tests | 6 PASS |
| Routing | 50/50 PASS |
| Behavior contracts | 10/10 PASS |
| Trajectory | 4 trajectories,52 turns PASS |
| Trajectory safety | 8/8 PASS |
| Problem facts harness | 42/42 PASS |
| Historical artifact harness | 27/27 PASS |
| Skill-only/self-contained | PASS within isolated development/tests |

First-run logs retain15 failures/38 errors from long Windows paths and
benchmark-output protection; the isolated replay resolves all but one.
The remaining failure is
test_2023e_feature_sets::test_real_q3_preserves_baseline_and_uses_controlled_folds,
whose manifest read-root guard sees this run's physical parent path. No test
source is changed or assertion bypassed. This extra scoped-path limitation is
separate from DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING.

The existing default collection issue remains recorded. Default repository-wide
pytest was not rerun because it would collect .tmp checkout and frozen duplicate
smoke modules. Those directories, historical outputs and pre-existing untracked
artifacts are not repaired or deleted. Explicit valid suites were used instead.

## Integrity And Claims

integrity-after.json verifies source hashes and every prior file covered by
integrity-before.json, with empty protected tracked diffs. Frozen Skill tree:
2b29e8ffa7c15d33bf81e675e8f1dcb240c226a6.
artifact-manifest.json binds committed artifacts to exact bytes, excluding
itself. Experiment, active evidence and source references are checked by the
frozen provenance helpers; the logical workspace's strict-isolation rejection
is retained in contract-audit.json. No OS-isolation PASS is claimed.

Final validity is PARTIAL, not an unrestricted optimal feasible network answer.
