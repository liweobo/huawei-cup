# Validation

The original data audit remains PARTIAL. Source bytes, body paragraphs and source object inventory are verified; missing actual map/OD/coordinates/congestion prevent official quantitative validation. `results/canonical-input-audit.json` uses null for unknown real row/error counts, never artificial zeros.

The structured PLANNED record was created and passed the unchanged Skill provenance validator before experimental computation. The executed record passes with status OBSERVED only for synthetic code verification; planned/executed normalized protocols match. The saved 8-subset enumeration rejects all 4 disconnected alternatives. Its 4 connected alternatives satisfy the declared static checks. Normal baseline/primary/redundant networks and 22 outage networks were generated; an independent reader reconstructed 33 saved networks including all eight alternatives.

Key numerical checks: manual 0->2 path length=5 versus direct arc 9; reverse 2->0=8; fourth node isolated; commodity balance residuals=0; route/arc cost disagreement below 1e-8 yuan/day. Capital and depreciation recompute from physical facilities once. Infeasible networks have null selectable objective. No solver status is extrapolated from the toy to the original problem.

The directional +50% artificial demand surge is a named generic scenario using the current `robustness.py`; it is not new measurement. The 5% given growth rate produces factors 1.477455443789063 at t=8 and 4.321942375150668 at t=30. Reference 5 departures/hour *18 hours gives 90 departures/day and full 8-carriage 5t trains give at most 3600 dispatched tonnes/day under A05, before mixed-service, trip, and timing restrictions. These upper bounds do not establish daily clearing or a real expansion date.

## Repository Checks

`validation-results/repository-checks.json` records exact commands, return codes, times and log paths. Existing `development/tests`: 305 passed, including skill-only self-contained tests. Nineteen standalone harnesses passed: routing, trigger, adversarial trigger, behavior contract, trajectory, trajectory safety, historical artifact, postmortem, problem facts, run001/run002/run003/run-attempt integrity, clean room, temporal availability, runtime binding, portable runtime, repository packaging and phase5.

DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING: unrestricted repository pytest failed collection with 44 import-file mismatches caused by `.tmp/github-publish-checkout`. No test code fix, cache deletion or duplicate-checkout modification was made.

EXISTING_SMOKE_FAILURES_PRESERVED: the all-Markdown smoke scanner reports the pre-existing 2022C placeholder and duplicates under frozen 2005D test workspaces and 2020A reference/frozen workspaces. These are not new Skill regressions. Full raw failure logs remain local and are excluded from commit; the checked-in `existing-environment-issues.json` retains hashes and representative lines. No historical source/fixture was edited to obtain a green run.

Before/after hashes in `integrity/` verify 744 protected tracked and existing nonignored untracked files. Both Skill trees equal `2b29e8ffa7c15d33bf81e675e8f1dcb240c226a6`. This is repository regression evidence, not proof that the unresolved 2017F original task has been solved.

Reproduction: use a fresh workspace copy of this run's `source/`, `code/`, and documents, with the recorded repository Skill at the frozen HEAD. Run `prepare_experiment.py`, the Skill `runtime_provenance.py validate-experiment`, `run_oracle.py`, then `independent_audit.py`. Do not overwrite this frozen run's records. Document extraction uses the bundled Python plus olefile 0.47, Aspose.Words 26.9.0 and PyMuPDF 1.28.2; numerical runs use Python 3.12.10, NumPy 2.5.2, SciPy 1.18.1 and the existing Skill dependencies.
