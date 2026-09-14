# Layer B Transcript Format

This directory stores real Skill/ChatGPT benchmark transcripts after a model
run. Do not create invented assistant answers and do not label synthetic
conversation as a real transcript.

Recommended file shape (model-visible fields only; expected routes and ground
truth stay in evaluator-only packages):

```yaml
benchmark_id: prediction_clean_01_run_001
skill_version: V2.6 Phase 6
model: <actual model identifier>
date: YYYY-MM-DD
problem_source:
  status: ACCEPTED | VERIFIED | MISSING | UNVERIFIED
  reference: <local source.yaml path for ACCEPTED, or verified source>
evidence_ledger: []
active_run_id: <current-run-id>
active_evidence_set: {}
turns:
  - turn_id: turn-001
    user: <verbatim user message>
    assistant: <verbatim assistant response>
    actual_route: analyze_problem
    state_before: {}
    state_after: {}
    artifacts_provided: []
    tool_calls: []
    claims: []
    evidence_refs: []
    evidence_created: []
    state_changes: []
    risks: []
    blocking_status: CLEAR
    next_action: <next highest-value action>
    protocol_disclosures: []
    evaluator_notes: []
model_behavior_p0: []
project_blockers: []
outcome: NEEDS_REVIEW
```

Preserve verbatim messages, model/version metadata, timestamps, source status,
and any artifacts referenced by the assistant. `ACCEPTED` records user-provided
artifacts without asserting official provenance; `VERIFIED` requires independent
source verification. Evidence references must resolve to the ledger, and
`EXPERIMENT_RESULT` claims require an observed `CODE_RUN` artifact. Never add
`expected_route`, `ground_truth`, or rubric fields to the model-visible script.

Validate a real transcript with:

```bash
python harness/model_behavior_evaluator.py benchmarks/transcripts/<actual-run>.yaml
```

The machine-readable field contract is in [`schema.yaml`](schema.yaml).

For the historical C-problem pressure test, `run-001` and `run-002` are
archived under `benchmarks/runs/historical_2024_c_core_loss/`. Their raw files
are evaluator-only immutable evidence. Run-002 remains `NEEDS_REVIEW` with
zero model-behavior P0 findings; the benchmark is `READY_FOR_RUN_003`, and
`run-003` must use the unchanged blind script plus an isolated run workspace.
Generated artifacts in future runs must be registered with stable artifact IDs;
cleanup is dry-run by default and cannot remove referenced or immutable evidence.
