# Evidence Ledger

All generated artifacts below are bound to `historical_2020_a_chip_phase_noise/run-001`. SHA256 values are filled by the final integrity command after all edits.

| Artifact ID | Path | Role | Status |
|---|---|---|---|
| source-2020a-docx | `source/2020A.docx` | official input | VERIFIED |
| source-provenance-json | `source/source-provenance.json` | URL/blob/SHA256 provenance | VERIFIED |
| extracted-docx-structure | `source/extracted/document-structure.json` | DOCX package audit | VERIFIED |
| problem-facts | `problem-facts.md` | frozen facts and ambiguity flags | VERIFIED |
| signal-ledger | `signal-ledger.md` | signal and frequency conventions | VERIFIED |
| preprocessing-record | `preprocessing-record.md` | preprocessing provenance | VERIFIED |
| algorithm-contract | `algorithm-contract.md` | input/output/math/complexity | VERIFIED |
| run-code | `code/run_blind_simulation.py` | reproducible implementation | VERIFIED |
| synthetic-checks | `work/synthetic_checks.json` | transform and unwrap checks | PASS |
| q1-results | `outputs/q1_summary.csv`, `outputs/q1_ber_curve.csv` | Q1 measurements | OBSERVED_WITH_LIMITATIONS |
| q2-results | `outputs/q2_overhead_grid.csv` | Q2 grid | OBSERVED_WITH_LIMITATIONS |
| q3-results | `outputs/q3_candidates.csv` | fixed-point/resource search | OBSERVED_WITH_LIMITATIONS |
| q4-results | `outputs/q4_tradeoff.csv` | exploratory tradeoff | OBSERVED_WITH_LIMITATIONS |
| order-sensitivity | `outputs/channel_order_sensitivity.csv` | model-order sensitivity | PASS |
| validation-report | `validation.md` | validation interpretation | VERIFIED |
| reviewer-report | `reviewer-report.md` | P0-P3 review | VERIFIED |
