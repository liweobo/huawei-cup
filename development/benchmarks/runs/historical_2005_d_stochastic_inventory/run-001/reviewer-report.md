# Reviewer Report

Overall Status: PASS WITH ONE GENERALIZABLE SKILL GAP AND DECLARED SOURCE LIMITS

## P0 Critical

| ID | Evidence location | Issue | Impact | Minimal fix | Recheck |
|---|---|---|---|---|---|
| P0-2005D-01 | `cost-ledger.md`, `problem-facts.md` | The source defines `c4` inconsistently (per lost item, per box-day, per volume-day) | A unique numerical shortage-cost objective does not exist without a chosen reading | Keep both readings as explicit scenarios; never publish a single c4-based answer as unconditional | Confirm no policy ranking flips between readings |

No other P0 finding. Capacity, conservation, state transition and cost accounting all pass, so no result in this run is invalidated.

## P1 Serious

| ID | Evidence location | Issue | Impact | Minimal fix | Recheck |
|---|---|---|---|---|---|
| P1-2005D-01 | `validation/ordered-protocol-probe.json`; `skill/scripts/runtime_provenance.py:51-65` | `normalize_protocol` sorts every list, so an ordered event protocol compares equal after its execution order is changed; `protocols_differ` returns `False` and the guard reports no error | The protocol-change guard silently passes a causally different step ordering; generalizes to queue, reliability, simulation, risk and finance event order | Preserve sequence when normalizing ordered stages; sort map keys only | Re-run the ordered-protocol probe on a corrected guard |
| P1-2005D-02 | `problem-facts.md`, `stochastic-ledger.md` | Q2 delivery histories are only 36/43/61 consecutive observations and their population law and stationarity are unknowable from the data | Q2/Q4 lead laws are estimates, so those optima are model-conditional | Report the empirical law as the estimate and bound the effect of dependence (done) | Treat any wider claim as needing more data |

## P2 Important

| ID | Evidence location | Issue | Fix |
|---|---|---|---|
| P2-2005D-01 | `validation/boundary-sensitivity.json` | Product 3's unconstrained optimum is an open-boundary cost infimum at L -> 40, not an attained optimum | Already disclosed; keep the integer optimum L = 39 distinct from the infimum |
| P2-2005D-02 | `validation/final-model-audit.json` | Discrete-uniform Q4 service probability sits at a numerical support boundary | Already labeled `ESTIMATE_UNSTABLE`; do not publish it as a service level |
| P2-2005D-03 | `source-provenance/README.md` | Word COM conversion failed (`REGDB_E_CLASSNOTREG`), so no page-level layout rendering was possible | Not content-bearing; re-render in an environment with Word or LibreOffice if page QA is required |

## P3 Polish

| ID | Evidence location | Issue | Fix |
|---|---|---|---|
| P3-2005D-01 | `development_tests.log` | This run's `--basetemp` was pointed inside `development/benchmarks`, which the harness correctly rejects, producing 9 self-inflicted errors | Point `--basetemp` outside protected trees on the next run |

## Required Evidence / Questions

- Intended resolution of the source `c4` unit conflict.
- Whether the Q2 delivery observations should be treated as iid or as a dependent process.
- Whether Q4's uniform lead time is continuous or integer-valued.
- Whether a page-level rendering of the source document is required for the benchmark record.

## Fix Order

Must Fix: keep the `c4` reading explicit whenever a number is reported.

Should Fix: preserve list ordering in the frozen Skill's protocol normalization (post-freeze, after human review).

May Defer: page-level rendering and the test `--basetemp` placement.

## Notes on This Run

The frozen Skill correctly rejected an early experiment record whose `protocol_change_disclosure` was missing required fields (`validation/attempt-001-record-failure.json`). That rejection was an authoring mistake in this run and is not a Skill gap. The run did not modify any Skill file, did not access any excellent-solution or answer material, and did not alter frozen historical assets.
