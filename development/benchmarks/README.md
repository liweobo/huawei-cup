# Historical Problem End-to-End Trajectory Benchmark

## Current Status

Historical development is complete: `HISTORICAL_PROBLEM_DEVELOPMENT_COMPLETE`.
Maintenance is limited to final release/readiness hardening; no new benchmark
is scheduled and problem 11 is prohibited. See the [closure and capability
inventory](../docs/historical-validation-closure.md) and [release checks](../docs/release-readiness.md).
All completed runs, source recoveries, reference benchmarks, and targeted
regressions under `runs/`, together with `run-attempts/`, are immutable evidence.
Keep their bytes, original decisions, manifests, and historical findings intact.

## What This Benchmark Tests

The deterministic Layer A runner tests the control plane of the math-modeling
Skill across multi-turn trajectories: trigger decisions, route transitions,
context carry-over, expected phases, lightweight Competition State updates,
blocking risks, workflow/Required Reads contracts, route coverage, and stable
trajectory length.

## What It Does Not Test

It does not generate assistant responses, prove that a model understood a real
problem, validate equations, run experiments, or establish that an LLM can
maintain high-quality evidence chains. Passing Layer A is not an end-to-end
LLM behavior pass.

## Layer A vs Layer B

Layer A is deterministic Python and can report PASS/FAIL. Layer B uses real
Skill/ChatGPT transcripts evaluated with [model-behavior-rubric.md](model-behavior-rubric.md).
The transcript format is defined in [transcripts/README.md](transcripts/README.md);
the read-only evaluator is `development/harness/model_behavior_evaluator.py`. No assistant
transcript is fabricated in this repository.

## Fixture Format and Source Gate

Trajectory files live in [trajectories/](trajectories/) and follow
[trajectories/schema.md](trajectories/schema.md). Historical entries must pass
the source gate. `ACCEPTED` is used for a user-provided, hash-checked package;
`VERIFIED` is reserved for independently verified official provenance. Both
are reported separately from synthetic demos and count as historical Layer A
coverage only after the gate passes. See [problems/README.md](problems/README.md).

The repository contains three Phase 2 synthetic trajectories and one accepted
user-provided historical trajectory. `run-001`, `run-002`, and `run-003` are
frozen real Layer B runs with retained structured transcripts, evidence
ledgers, evaluations, postmortems, and selected observed artifacts. The
original transfer-archive metadata is recorded in each manifest; archives are
not live workspaces. All three evaluator-only outcomes are `NEEDS_REVIEW` with
zero `MODEL_BEHAVIOR_P0` findings. Run-003 retains a P1 filesystem-visibility
finding. The first Run-004 launch attempt is recorded separately under
`run-attempts/`; it aborted before Turn 1 because platform transport and
runtime-root binding could not be verified. This is the archived
behavioral-platform track: `BLOCKED_BY_PLATFORM` describes that attempt,
not current release readiness. Historical completion does not require Run-004.

## Runtime Provenance

Real experiments use a fresh run-scoped workspace at
`runtime/<benchmark-id>/<run-id>/`. `workspace-manifest.yaml` records immutable
input hashes, allowed read roots, and the only writable root. The
`active-evidence-set.yaml`, Experiment Record, and Evidence Ledger select and
hash the evidence consumed by a paper. Frozen historical runs remain
evaluator-only and are not used as a live workspace.

## Problem Families

The fixtures cover prediction/time-series, optimization/decision, and
evaluation/simulation/mechanism. The schema is intentionally not tied to one
model family.

## Route and Phase Semantics

Layer A maps routes to observable phases without enforcing a finite-state
machine:

| Route | Phase |
|---|---|
| select_problem | selection |
| analyze_problem | problem_analysis |
| audit_data | data |
| build_baseline | baseline |
| design_model | modeling |
| run_experiment | experiment |
| validate_model | validation |
| write_paper | writing |
| reviewer | review |
| final_check | submission |

Valid iterations such as `validate_model -> design_model` and
`reviewer -> write_paper` are allowed. A return from `final_check` to
`select_problem` is suspicious unless a new blocking risk is present. The
runner records these decisions; it is not a full workflow engine.

## Run-001 Postmortem

The frozen package metadata lives under
`runs/historical_2024_c_core_loss/run-001/` and
`runs/historical_2024_c_core_loss/run-002/`. Their transcripts and selected
evidence are SHA256-checked retained inputs. Run-001's first meaningful
failure is Turn 3's contradictory duplicate count (`0` versus the observed
canonical value `1`), caused by composing a response from non-canonical audit
stages. Run-002's first meaningful failure is Turn 8's expanded validation
protocol without a structured runtime Experiment Record or explicit
plan-to-execution disclosure. Run-002 also exposes a fresh-workspace/evidence
versioning failure. These are P1 quality/state or benchmark-infrastructure
findings, not model-behavior P0. Canonical audit consistency, protocol
provenance, run isolation, evidence versioning, and raw workbook fact
regressions are deterministic.

## How to Run

From the repository root:

```bash
python development/harness/trajectory_test.py
python development/harness/postmortem_regression_test.py
python development/harness/problem_facts_test.py
python development/harness/run001_integrity_test.py
python development/harness/run002_integrity_test.py
python development/harness/phase5_regression_test.py
```

The complete active verification sequence is in [development/README.md](../README.md).
Live documentation smoke excludes frozen run/attempt Markdown; source,
manifest, evidence hashes, and run integrity remain independently checked.

## Archived Behavioral-Platform Track: Portable Runtime Handoff

V2.8 exports the shared clean-room allowlist into an independently validated
runtime directory and optional ZIP. The developer/evaluator tree is not an
execution dependency. Infrastructure reports and transport evidence remain
host-side; model tools read only the exported project and write under its
workspace. At the archived attempt, no usable binding/transport backend had
been verified; a compatible external runner was required for that track.

The archived plan reserved `run-004` / `run-004-attempt-002` for a possible
retry. That reservation is not an active schedule or release requirement.
The aborted `run-004-attempt-001` and earlier runs retain their outcomes.
Exporting, validating, packaging, and deterministic regressions create no
retry or model response.

## Metrics

The runner reports Trigger Accuracy, Route Accuracy, Context Retention,
Transition Accuracy, Risk Detection, Route Coverage, Longest Stable Trajectory,
and the count of ACCEPTED/VERIFIED historical trajectories. Metrics remain separate and
interpretable; no composite score is manufactured.

## P0 Failures

Layer A blocks invalid state such as unresolved P0 risk with `COMPLETE`, fake
experiment completion without observed evidence, invalid phases/statuses, and
unverified historical coverage. Layer B P0 definitions are in the rubric and
the transcript evaluator also checks evidence references, observed run artifacts,
and evaluator-only field separation.

Passing the deterministic trajectory benchmark does not prove that an LLM will
produce high-quality mathematical modeling answers.

## Closed Historical Development Policy

Do not add a historical problem, reopen excellent papers, reinterpret prior
decisions, or start another reference benchmark. Retained source gates,
blind scripts, and runtime adapters document the completed work and archived
platform attempt. Maintain active documentation, reproducible tests, and
distribution checks only; await human release review after readiness closes.
