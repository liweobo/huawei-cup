# Release Readiness

`RELEASE_READINESS_COMPLETE` — verified 2026-09-23 against historical main base
`79f505df99960ab6aa988d9138dfd28079b6252d`. The [closure record and single
capability inventory](historical-validation-closure.md) preserve graduation
`PASS`, overall `STRONG`, and top generalizable gap `NONE`.

## Validation Results

| check | result |
|---|---|
| Python requirement / tested runtime | >= 3.10 / CPython 3.13.1, Windows |
| Clean declared dev environment | `CLEAN_DECLARED_DEV_ENVIRONMENT_PASS`; fresh `.tmp/release-venv`, installed only `requirements-dev.txt`; `pip check` PASS |
| Default pytest command | `python -m pytest -q`: **341 passed**, 63.84 seconds |
| Active harness suite | **21/21 PASS**, exactly the existing `harness/*_test.py` entry points in [development commands](../README.md) |
| Test inventory reconciliation | Added the previously omitted protocol-order command; no missing, duplicate, nonexistent or historical temporary test entry; three support modules excluded |
| Compilation | `python -m compileall -q development/harness development/tooling development/tests skill/scripts`: PASS |
| Live smoke | PASS, **65 Markdown files / 10 routes** |
| Scope regression | **19 tests PASS**: broken live links fail; frozen generated content is excluded; empty/unfinished/duplicate live content still fails; findings reach CLI failure status |
| Frozen integrity | Historical artifact, problem facts, run001/run002/run003 and run-attempt integrity harnesses PASS; all protected byte hashes identical |
| Skill-only isolation | Copy and ZIP extraction both PASS: 48 Markdown files, all route/default resources and inline resource mentions resolve inside Skill; all 17 Python files compile and helper modules import |
| Isolated behavior | Existing ordered-protocol and evaluation-semantics behavior checks PASS in both copies; actual release ZIP extracted and rechecked in new system temporary directories |
| Active docs / absolute paths | PASS; portable root instructions, archived platform status, no personal installation paths in active overviews, development docs or Skill Markdown |

The fresh environment resolved numpy 2.5.3, pandas 3.0.6, scikit-learn 1.9.1,
openpyxl 3.1.5, matplotlib 3.11.2, pytest 9.1.1 and PyYAML 6.0.3 (scipy 1.18.1).
Dependency declarations were sufficient and unchanged. Checks used
`PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`, and `PYTHONPYCACHEPREFIX` under
`.tmp/release-readiness/pycache`; no generated output was written into Skill
or frozen evidence. The historical `DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING`
record remains intact.

## Frozen Evidence and Smoke Boundary

Live smoke excludes only the frozen `development/benchmarks/runs/**` and
`development/benchmarks/run-attempts/**` trees in addition to its existing
generated-output exclusions. Active README, AGENTS, Skill, development docs,
rules, references and workflows remain checked, including links into history.
Independent integrity tests still require historical source/manifests and
verify retained hashes. No historical run, report, validation, manifest,
visibility report, draft marker, link, formatting or line ending was edited.

Before the scope change this host reported five frozen Markdown keyword
findings; older evidence still records its original four smoke/path findings.
Neither count is rewritten into a historical success.

Per-file SHA256 snapshots before and after covered **1,110 tracked benchmark
assets** (all tracked `development/benchmarks` files except its active README),
plus every existing local file in the frozen runs/attempts: **30,735 files**
in that broader snapshot. Both path sets and every digest were identical.
The broader count includes pre-existing ignored local recovery/runtime files.

| protected content | before = after |
|---|---|
| Tracked benchmark aggregate SHA256 | `4b3935315a9733e29a56ed2a8670a74c41df73e55434ce0f4a5425b7230928ef` |
| Broader local snapshot SHA256 | `0c93395fee08a708ca76f8f21d147d729c3d474368f08fc4213b6ce2b8b288ed` |
| Frozen runs Git tree | `66d2047b796726852ce04bed995a487cadf35a84` |
| Frozen run-attempts Git tree | `8de29a73c618363b9e8739a240b267188ce66159` |
| 2023E problem/evidence Git tree | `1d86b7ece9f07b6c9d67d9f82d7553758a13fade` |

Aggregate definition: sort repository-relative POSIX paths; concatenate
`path + NUL + SHA256(file bytes) + LF` as UTF-8, then SHA256 that stream.
For the portable tracked aggregate, enumerate `git ls-files -z development/benchmarks`,
omit only `development/benchmarks/README.md`, and hydrate Git LFS first.
The base commit permanently identifies each original blob/LFS object;
temporary per-file snapshots and execution logs were retained under
`.tmp/release-readiness/` and are not release dependencies.

## Skill and Packaging

The final **73-file tracked Skill tree SHA256** is
`c6d4833778939718dc7fecab34dd2a6549ac2a51d442d6f63646466311da0b38`
using the same aggregate definition over `git ls-files -z skill`.
Its base value was `6ec4b91dffa5f601899b89e60929a9f43614ee5d286098d6953f800467d754cb`.
The sole Skill edit replaces the nonexistent README AAR navigation with the
existing package-local AAR section. Scripts, rules, routes, contracts,
reviewer codes and Iron Rules are unchanged; applicability guidance was not
expanded. Version stays `V2.9 Phase 3`:
`VERSION_POLICY_UNCHANGED_NO_CANONICAL_RELEASE_SCHEME` (history and tags provide
no canonical release-bump scheme).

Skill dependency search found only the existing historical-path rejection
and the caller-supplied runtime-root argument in `runtime_provenance.py`.
Neither reads a developer repository. No development, benchmark, Git or
personal-path runtime dependency exists.

Both temporary packages were built with the existing
[`package_repository.py`](../tooling/package_repository.py). Skill-only has
**81 entries / 73 files**, only `skill/` at top level, and ZIP SHA256
`1de73d55219e65997af523f91e375e9c1384651284faf482170d39dde1850552`.
It contains no development, historical runs, Git data, outputs or caches.
The developer package contract also passed with **1,463 entries** under only
`huawei-cup-2026/`; this was a temporary packaging check, not a publication.
Both archives passed CRC, exact/case-folded duplicate-path, absolute/drive-path,
parent traversal, symlink/reparse-point and cache checks. The packager also
rejects linked source paths. Package files remain ignored development artifacts.

## Final Status

```yaml
historical_problem_development: COMPLETE
problem_11_required: NO
skill_semantic_changes: DOCUMENTATION_ONLY
historical_assets_unchanged: YES
routes: 10
clean_dev_environment: PASS
pytest: PASS
active_harness_suite: PASS
live_smoke: PASS
frozen_historical_integrity: PASS
skill_only_self_contained: PASS
skill_only_package: PASS
portable_docs: PASS
stale_current_status_removed: YES
release_blockers: 0
remaining_p2_items: terse predictive-surrogate applicability wording
final_status: READY_FOR_RELEASE
```

The retained P2 item and source/model limitations remain bounded as recorded
in the closure; partial uncertainty coverage is not a new P2 finding.
No new guard, helper, contract, modeling capability or
historical benchmark was added. Readiness work ends here; await human release
review, with no problem 11 or new benchmark scheduled.
