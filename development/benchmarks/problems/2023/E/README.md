# User Provided Historical Benchmark 2023 E

This directory registers the user-provided 2023 Chinese Graduate Mathematical
Modeling Competition E problem, Hemorrhagic Stroke Clinical Intelligent
Diagnosis and Treatment Modeling.

The package is `ACCEPTED` for reproducible testing only. The user supplied the
problem statement, concept note, original RAR archive, and the five extracted
Excel workbooks. `official_provenance: UNKNOWN` is intentional and is not a
claim that the package was independently verified against an official source.

The files under `raw/` are byte-for-byte copies of the supplied files. The RAR
archive is retained for provenance; the five extracted workbooks are the
canonical raw inputs used by the audit and baseline run.

The first pressure-test run is stored under
`../../runtime/historical_2023_e_hemorrhagic_stroke/run-001/`. It contains only
run-scoped code, reports, evidence records, and observed outputs. No result is
copied from the 2024/C benchmark.
