# Validation record

## Forecast-specific execution

- `run_analysis.py`: PASS; regenerated all retained CSV/JSON outputs from the retained source archives.
- `test_analysis.py`: `3 passed`.
- Synthetic guards: PASS for future target/weather leakage, post-origin rolling input, random split, recursive observed-target leakage, full-series scaler fit, reversed-time protocol, and proxy/MOR semantic promotion.
- Common origins: PASS (43 per AMOS horizon/method; 30 per highway horizon/method).
- Horizon metrics: PASS; no pooled-only score.
- Interval coverage: PASS; measured on 33 airport and 20 highway post-calibration origins per cell.
- Source byte integrity: PASS; all six `git hash-object` values equal supplied blob SHAs and all SHA-256 values equal the provenance ledger.

## Repository regression

- Effective Python environment (final rerun): `321 passed in 33.47s`.
- All routing, trigger, behavior-contract, trajectory, historical-integrity, problem-facts, temporal-availability, runtime-binding, portable-runtime, packaging, and phase-5 harnesses pass.
- Route coverage remains `10/10`.
- Compile-all: PASS for harness/tooling/tests/Skill scripts and this run’s code.
- Skill-only package: PASS; 81 entries, all under top-level `skill/`.

## Known pre-existing environment/findings

- `DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING`: default `D:\pyhton3.13\python.exe` has no `pytest`; the established isolated environment was used for effective tests.
- Structural smoke retains four frozen findings and was not modified:
  - `historical_2022_c_buffer_scheduling/run-002/REPORT.md`
  - `historical_2017_f_underground_logistics_network/run-001/REPORT.md`
  - `historical_2017_f_underground_logistics_network/run-001/validation.md`
  - `historical_2007_a_food_safety_evaluation/run-001/validation-results/README.md`

These findings predate this run and are outside the authorized scope.

## Outcome validation

- Same-time estimation and future forecasting are separated: PASS.
- Formal Q4 absolute MOR/dispersal-time output: NOT VERIFIED because the highway attachment has no absolute labels/calibration.
- Q2: NOT EXECUTED because the airport video is unavailable.
- Blindness: no excellent paper opened; the unintended non-substantive search-result snippet is disclosed and contributes to `PARTIAL` rather than being treated as solution evidence.
