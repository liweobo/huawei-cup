# Current 2022C Solution Freeze

This file freezes the current Skill evidence before reading the excellent
solution set. It is not revised after exposure to the references.

## BLIND_SOLUTION

- **Run**: `historical_2022_c_buffer_scheduling/run-002`.
- **Problem interpretation**: source-order vehicles pass through six FIFO
  inbound lanes, one return lane, a receiving transfer machine, and a
  delivery transfer machine; the final sequence and completion time are
  scored by the four stated objectives.
- **Decision variables**: inbound/return occupancy, transfer-machine
  actions, source consumption, and final assembly order.
- **State representation**: second-by-second discrete-event state with
  lane positions, return positions, machine availability, pending receive,
  and output order.
- **Hard constraints**: capacity, FIFO/inbound direction, machine
  non-interruption, return-to-home timing, Q1 priority rules, no direct
  return-to-assembly delivery.
- **Objective**: realized schedule score
  `0.4*O1 + 0.3*O2 + 0.2*O3 + 0.1*O4`.
- **Baseline**: source-order constructive policy.
- **Candidate representation**: mostly `STATE_COUPLED` event transitions,
  plus a late target-sequence experiment that was not truly coupled.
- **Search strategy**: deterministic source-order, greedy dispatch, and a
  bounded abstract target-sequence adjacent-swap experiment.
- **Return-lane handling**: legal actions exist but the selected best-found
  outputs use the return lane zero times.
- **Feasibility mechanism**: event simulator with hard-rule checks followed
  by an independent workbook audit.
- **Incumbent rule**: the implemented script selected the higher feasible
  weighted score, but the chosen search had poor objective coverage.
- **Validation**: independent workbook checks for codes, position occupancy,
  final receipt, and completion.
- **Result**:
  - Q1 weighted `53.367`, O1 `0`, O2 `80`, O3 `100`, O4 `93.67`;
  - Q2 weighted `53.643`, O1 `0`, O2 `81`, O3 `100`, O4 `93.43`.
- **Limitations**: no global optimum claim, O1 zero, no active return-lane
  resequencing, no search over meaningful future states.

## POSTFIX_STATE_COUPLED_SOLUTION

- **Run**: `historical_2022_c_buffer_scheduling/run-003-postfix`.
- **Problem interpretation**: unchanged from run-002.
- **Decision variables**: same complete state machine plus a legal-action
  policy choice at each event.
- **State representation**: real PBS state; the policy enumerates
  `legal_delivery_actions()` and applies the complete frozen event loop.
- **Hard constraints**: unchanged; illegal actions are not expandable.
- **Objective**: realized objective from `detailed_scores()`.
- **Baseline**: run-002 feasible best-found.
- **Candidate representation**: `STATE_COUPLED`.
- **Search strategy**: deterministic state-coupled priority policy, not a
  generic metaheuristic.
- **Return-lane handling**: the candidate can and does use the return lane;
  Q1 uses it for five actions in the regression.
- **Feasibility mechanism**: complete event loop plus an independent
  workbook audit.
- **Incumbent rule**: only feasible candidates participate; no surrogate
  replaces the realized score.
- **Validation**: `result31.xlsx` and `result32.xlsx` independently audited
  with zero hard violations.
- **Result**:
  - Q1 weighted `51.801`, O1 `0`, O2 `80`, O3 `94`, O4 `90.01`;
  - Q2 weighted `53.058`, O1 `0`, O2 `80`, O3 `100`, O4 `90.58`.
- **Limitations**: state coupling is verified, but the local action policy
  is myopic; no improvement phase, lookahead, or structured neighborhood.
