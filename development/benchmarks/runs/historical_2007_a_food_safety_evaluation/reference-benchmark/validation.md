# Validation Record

## Reference review

- Discovered files: `6` PDFs in the user-designated excellent-solution directory.
- Independent contents: `5`; `10052A.pdf` and `9005210.pdf` have identical extracted text.
- Full-text review: `164` file-pages extracted and read.
- Visual review: `39` selected pages rendered and inspected, covering every document's identity/opening page and its material formulas, tail method, threshold/standard evidence, result, limitation, or conclusion pages.
- Extraction assessment: `GOOD_WITH_EQUATION_LAYOUT_CAVEATS`; formula and table claims were checked against rendered pages rather than accepted from text layout alone.
- Award verification: `0/6`; all award levels remain `UNKNOWN`.

## Artifact checks

- All required comparison/report artifacts are present.
- `completion.json`, `pre-reference-freeze.json`, and `integrity.json` parse as JSON.
- The pre-reference `current-skill-solution.md` SHA256 remains `8c82f180a7cdc3619e9bc349adfd841b3311c899a73fe273ec7c4b5dbd428d6e`.
- All six downloaded PDF SHA256 values match `source-ledger.md`.
- The duplicate-content text hash matches for `10052A.pdf` and `9005210.pdf`.
- PDFs, extracted text, and rendered pages remain under ignored `.tmp/` and are not commit artifacts.

## Repository tests

Using the existing ignored run-scoped virtual environment and `PYTHONDONTWRITEBYTECODE=1`:

```text
development/benchmarks/runs/historical_2007_a_food_safety_evaluation/run-001/.tmp/venv/Scripts/python.exe -m pytest -q
305 passed in 36.57s
```

This full suite includes the current routing, behavior-contract, trajectory, problem-facts, historical-integrity, repository-packaging, and skill-only/self-contained tests.

The default interpreter remains an acknowledged environment issue:

```text
python -m pytest -q
D:\pyhton3.13\python.exe: No module named pytest
```

Classification: `DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING`. It was recorded and not repaired.

The current smoke scanner reports four frozen placeholders:

- `development/benchmarks/runs/historical_2022_c_buffer_scheduling/run-002/REPORT.md`
- `development/benchmarks/runs/historical_2017_f_underground_logistics_network/run-001/REPORT.md`
- `development/benchmarks/runs/historical_2017_f_underground_logistics_network/run-001/validation.md`
- `development/benchmarks/runs/historical_2007_a_food_safety_evaluation/run-001/validation-results/README.md`

These are existing frozen path/smoke conditions. No historical file or test infrastructure was changed to obtain a green smoke run.

## Result

`PASS_WITH_ACKNOWLEDGED_EXISTING_ENVIRONMENT_ISSUES`

All actionable tests pass. The post-hoc evidence supports the reported decision without changing the frozen Skill or blind run.
