# 2022C Stateful Scheduling Post-Fix Regression

## Scope

This is a targeted regression for the new
`stateful scheduling search contract`, not a new blind run. It reads the
frozen run-002 inputs and model but writes only under `run-003-postfix`.
No excellent paper, solution, answer, or third-party 2022C code was accessed.

## Contract

- `problem_type`: `STATEFUL_SCHEDULING`
- `candidate_representation`: `STATE_COUPLED`
- `feasibility_mode`: `BY_CONSTRUCTION`
- legal actions: `dispatcher.legal_delivery_actions()` evaluated on the
  current PBS state;
- transition: the complete frozen run-002 event loop, including lane motion,
  machine occupancy, pending receives, hard invariants and terminal test;
- objective: `detailed_scores()` on the realized simulated schedule.

The run-003 model copy contains an additive `action_policy` hook. The source
model SHA256 is `be7b0e1ccd489f24d0bc6c121b3bdcaf267e2aa25ee58582a20bd8c4984703d6`;
the state-coupled copy SHA256 is
`22b7be3d5ebd22d6148790f8e013351dd62be181fcaf6f7ccfe9db5926d543fc`.

The copy also fixes two latent behavioral issues exposed only when the
state-coupled policy uses the return lane:

1. return-lane movement must advance from position 1 toward 10;
2. blank output cells mean the vehicle is outside the 74 coded regions and
   must not inherit a stale region after a transition.

These are regression-copy corrections. Run-002 remains byte-for-byte frozen
and its published conclusions are unchanged.

## Formal Comparison

| scenario | old best-found | new state-coupled | old O1 | new O1 | new hard violations | feasible |
|---|---:|---:|---:|---:|---:|---:|
| Q1 | 53.367 | 51.801 | 0 | 0 | 0 | true |
| Q2 | 53.643 | 53.058 | 0 | 0 | 0 | true |

The state-coupled candidate is real and auditable, but it does not improve
the stated weighted objective in this iteration. This is not a contract
failure: the contract fixes search validity and coupling, not solution
quality.

## Independent Audit

`audit-postfix.py` re-opened `result31.xlsx` and `result32.xlsx`, checked
the full matrix, allowed region codes, position occupancy, final assembly
receipt and completion. Both files report:

```text
code violations = 0
position violations = 0
receipt violations = 0
status = FEASIBLE
```

## Status

```text
STATEFUL_SCHEDULING_SEARCH_READY
candidate_representation: STATE_COUPLED
formal_candidate_feasible: YES
hard_violations: 0
objective_improved: NO
state_coupling_verified: YES
run_002_unchanged: YES
```
