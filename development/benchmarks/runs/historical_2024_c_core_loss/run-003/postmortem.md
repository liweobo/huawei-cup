# Run-003 Postmortem

## Outcome

- Behavioral outcome: `NEEDS_REVIEW`
- Model-behavior P0 findings: none
- Project blockers: 8
- Workspace isolation: `FAIL`

## What worked

1. Turn 3 used the canonical audit and retained the observed one duplicate row without the Run-001 contradiction.
2. Q1 baseline and model-comparison runs were real, hash-checked and bound to `run-003`.
3. The transcript consistently separated labeled internal validation from unlabeled Attachment 2 predictions.
4. Q4 alignment was not mislabeled as a loss prediction, and final-check correctly returned `NOT READY`.

## Regression finding

The manifest declared `prior_run_artifacts_visible: false`, but a model command using `rg --files benchmarks/runtime` exposed a historical `run-002` path. No evidence shows that old numeric results were consumed; the visibility failure is nevertheless retained as an infrastructure regression.

## New pattern

Repeatedly useful behavior is explicit evidence-bound wording: observed metrics, predictions, author definitions, and `NOT RUN` values are named separately before paper review.

## New trap

A run-scoped manifest alone does not guarantee filesystem listing isolation. The harness/runtime must constrain repository enumeration as well as write paths and declared read roots.

## Missing or outdated rules

- No new universal Skill rule is promoted from this single run.
- The isolation contract needs an infrastructure-level fix or regression test; this is separate from model-behavior scoring.
- No outdated competition rule was identified. 2026 compliance remains `UNVERIFIED`.

## Required next action

Hide evaluator-only historical archive paths from model-visible enumeration, then repeat the unchanged 14-turn script in a fresh run before treating workspace isolation as resolved.
