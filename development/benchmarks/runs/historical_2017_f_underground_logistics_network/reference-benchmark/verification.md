# Verification And Historical Protection

## Immutable Inputs

`pre-reference-freeze.json` was created before downloading/reference methods.
It records the starting HEAD, Skill and all2017F sibling tree hashes, current
solution summary SHA256, and tracked/nonignored prior files plus prior integrity
and original-source bytes. The post-hoc verifier rehashes this set and checks
that tracked changes and new nonignored files stay inside reference-benchmark.

Protected: Skill;2017F run-001,source-recovery,run-002-source-complete;2005D
run-001/run-002/reference-benchmark;2020A,2011B,2022C,2023E,2024C assets.
Existing untracked historical outputs are neither staged, deleted nor repaired.
Ignored browser/extraction caches elsewhere are not cleaned. No blind-run
summary is retrospectively rewritten after reading references.

## Verification Commands

From this directory:

```text
python -X utf8 -B code/verify_benchmark.py --write
python -X utf8 -B code/verify_benchmark.py
python -X utf8 -B code/verify_benchmark.py --target index
python -X utf8 -B code/verify_benchmark.py --target head
```

`--write` writes only formula-checks.json,integrity-verification.json and
artifact-manifest.json here. The other modes are read-only. Index and HEAD
modes compare every manifest-listed artifact and the manifest itself against
Git bytes, and forbid extra tracked cache/PDF files. No reference program,
facility search, routing solver, timetable or expansion model is executed.

The seven PDFs are verified against pinned Git blobs,SHA256 and sizes. Review
metadata agrees with extracted page counts and33 logged visual inspections.
PDFs are not necessary to read the committed report; they can be downloaded
from pinned URLs when reproducing the hash verification.

## Tests And Environment

Actual commands/results are in `test-record.json`. This stage runs the existing
historical artifact harness and six local archive/arithmetic tests. It does
not rerun expensive model solves. The304 development passes and one existing
enclosing-path/path-guard failure remain **inherited frozen evidence**, not a
newly claimed full regression run. Relevant frozen record:
`../run-002-source-complete/validation.md` and `validation-results/summary.json`.

`DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING`, `.tmp/github-publish-checkout`,
frozen2020A smoke duplicates and path issues remain untouched. A direct pytest
attempt with the bundled document Python also found no installed pytest; that
runtime limitation is recorded separately. The existing Python3.12 installation
is used for tests, without installing packages or changing the repository.
Bytecode writing and pytest's cache provider are disabled; temporary test files
are confined to ignored `work/`.

## Commit Scope

Only this reference-benchmark directory's metadata,reports and audit helper
code are eligible. `work/`,PDFs,page renders,extraction/OCR cache,`.tmp` and
`__pycache__` are excluded. The artifact manifest excludes itself to avoid a
self-hash cycle. Git stage/HEAD verification closes that one-file exception.
Commit message: `benchmark: compare 2017F against excellent solutions`.
Push uses the existing branch without force; final response reports remote SHA.

The integrity manifest covers exact bytes, not proof that every mathematical
interpretation is correct. Semantic uncertainty is retained in the comparisons
and completion record.
