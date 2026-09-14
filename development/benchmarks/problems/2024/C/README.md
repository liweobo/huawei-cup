# User-Provided Historical Benchmark: 2024 / C

This directory contains the five raw files explicitly provided by the user for
the Phase 3 benchmark. The raw files are copied byte-for-byte into `raw/` and
registered in `source.yaml` with SHA256 hashes.

`benchmark_source_status: ACCEPTED` means the artifact was user-provided and
preserved for benchmark use. It does not mean that the assistant independently
verified official provenance. `official_provenance: UNKNOWN` is intentional.

Model-visible material is limited to the raw problem and attachment files plus
the blind user script. Evaluator-only material is stored separately in
`ground-truth.yaml`, `problem-facts.yaml`, and `expected.yaml`.
