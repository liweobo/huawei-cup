# Problem Facts: 2022 C PBS Resequencing

This document is a frozen reading of the statement in
`run-001/extracted/problem.txt` and attachments 1-4. It distinguishes direct
statement facts from adopted interpretations of ambiguous wording.

## Background

- **FACT BG-01**: The production system includes welding, painting and final
  assembly shops with different sequencing preferences.
- **FACT BG-02**: A painted-body store (PBS) sits between painting and final
  assembly and changes the painting output sequence into a final-assembly
  input sequence.
- **FACT BG-03**: Daily production volume is 200-450 vehicles; there are two
  model classes and about ten colors.
- **FACT BG-04**: The specified system has one paint-PBS exit, one receiving
  transfer machine, six inbound lanes, one return lane, one delivery transfer
  machine and one PBS-final-assembly receiving point.
- **FACT BG-05**: Each inbound lane has 10 FIFO positions. The single return
  lane has 10 positions. Lane pitch is 2 m plus 1 m gap; transfer speed is
  uniform.

## Objects And State Space

- **FACT OBJ-01**: Input is a painting output sequence list. Multiple lists
  may be supplied.
- **FACT OBJ-02**: The output is, for every vehicle and every second, the
  region occupied among paint-PBS exit, receiving transfer machine, any inbound
  lane position, any return lane position, delivery transfer machine, or
  PBS-final-assembly receiving point.
- **FACT STATE-01**: The output matrix uses 74 region codes from Attachment 3.
  Blank means the vehicle is outside all 74 regions.
- **FACT STATE-02**: If one vehicle is simultaneously in multiple regions under
  the zero-time load/unload assumptions, the matrix records the **last region**
  in the transition.
- **FACT STATE-03**: The matrix example is 50 vehicles by 100 seconds in
  Attachment 4, but this is only a template demonstration.

## Move Rules

- **FACT MOVE-01**: The receiving transfer machine moves bodies from the
  paint-PBS exit to a suitable inbound lane, and from the return lane to a
  suitable inbound lane.
- **FACT MOVE-02**: The delivery transfer machine moves bodies from inbound
  lane position 1 to the PBS-final-assembly receiving point, and moves bodies
  requiring resequencing from inbound lane position 1 to return-lane position
  1.
- **FACT MOVE-03**: The delivery transfer machine cannot move a body from the
  return lane directly to PBS-final assembly.
- **FACT MOVE-04**: Inbound and return lanes move only in the diagrammed
  direction.
- **FACT MOVE-05**: Each transfer machine carries at most one body at a time.
- **FACT MOVE-06**: After any operation each transfer machine must return to
  its central initial position before the next operation.
- **FACT MOVE-07**: A transfer-machine operation cannot be interrupted.
- **FACT MOVE-08**: If return-lane position 10 has a body and the receiving
  transfer machine is idle, that body has priority to be processed.
- **FACT MOVE-09**: If several inbound lanes have a body at position 1 and the
  delivery transfer machine is idle, the body that first reached position 1
  has priority.
- **FACT MOVE-10**: If any inbound lane position 1 is occupied, the delivery
  transfer machine cannot be left idle.
- **FACT MOVE-11**: Every inbound lane and the return lane hold at most 10
  bodies; each position holds at most one.
- **FACT MOVE-12**: Bodies in different positions may move non-synchronously.
- **FACT MOVE-13**: When the position immediately downstream of a body becomes
  empty, the body must immediately start moving one position downstream.
- **FACT MOVE-14**: A body cannot be scheduled while it is moving between
  positions.

## Timing

- **FACT TIME-01**: Loading from a transfer machine to inbound position 10 or
  return position 1, and loading from inbound position 1 or return position 10
  to a transfer machine, takes zero time.
- **FACT TIME-02**: Loading a body from the paint-PBS exit to the receiving
  transfer machine, and unloading from the delivery transfer machine at the
  PBS-final-assembly point, takes zero time.
- **FACT TIME-03**: The paint-PBS exit is centrally located opposite inbound
  lane 4. For a receive-and-return operation to inbound lanes 1-6, the stated
  operation times are `[18, 12, 6, 0, 12, 18]` seconds.
- **FACT TIME-04**: For delivery from inbound lanes 1-6 to PBS-final assembly,
  the stated times are `[18, 12, 6, 0, 12, 18]` seconds.
- **FACT TIME-05**: For delivery from inbound lanes 1-6 to return-lane
  position 1, the stated times are `[24, 18, 12, 6, 12, 18]` seconds.
- **FACT TIME-06**: For moving a body from return position 10 to any inbound
  position 10, the stated receive-and-return times are
  `[24, 18, 12, 6, 12, 18]` seconds.
- **FACT TIME-07**: A body moving one position in an inbound or return lane
  consumes 9 seconds.

## Adopted Operational Interpretation

- **AMBIGUOUS OP-01 / ADOPTED A-01**: The statement gives operation duration
  including the carrier's return to the central home position. The discrete
  event model therefore commits the carrier for the listed duration; the
  vehicle load/unload position transition itself is instantaneous under
  TIME-01/TIME-02. This matches MOVE-06 and the fact that no separate return
  time is listed.
- **AMBIGUOUS OP-02 / ADOPTED A-02**: Lane motion is autonomous once the
  downstream position is empty, per MOVE-13. The implementation advances all
  eligible lane movements at each 9-second lane-move epoch and does not add a
  separate machine decision for those movements.
- **AMBIGUOUS OP-03 / ADOPTED A-03**: "First reached position 1" in MOVE-09 is
  represented by a monotone arrival timestamp at position 1. The delivery
  machine is never deliberately idled when a position-1 body exists.
- **AMBIGUOUS OP-04 / ADOPTED A-04**: The vehicle can be recorded in the final
  assembly receiving point at the operation completion time; it leaves that
  region after the next integer second. This produces a time-one region while
  preserving the required final completion time.
- **AMBIGUOUS OP-05 / ADOPTED A-05**: Return-lane use count increments once
  whenever the delivery machine moves one body from an inbound lane position 1
  to return position 1.

## Objective Functions

- **FACT OBJ1-01**: Weight 0.4. Start at 100. Traverse the final output
  sequence and, for every consecutive pair of hybrid bodies, count the number
  of non-hybrid bodies between them; subtract 1 for every count not equal to 2.
- **FACT OBJ2-01**: Weight 0.3. Start at 100. Partition the final sequence
  according to the statement: if it starts with 4WD, cut at every 2WD-to-4WD
  change; if it starts with 2WD, cut at every 4WD-to-2WD change. Subtract 1 for
  every block whose 4WD:2WD ratio is not 1:1.
- **FACT OBJ3-01**: Weight 0.2. Start at 100. Subtract 1 for every return-lane
  use.
- **FACT OBJ4-01**: Weight 0.1. Start at 100. Let `C` be output-queue length,
  first entry into the paint-PBS exit time 0, and `T` the time at which the
  last body reaches PBS-final assembly. Theoretical minimum is `9C + 72`.
  Time penalty is `0.01 * (T - 9C - 72)`, and objective 4 score is
  `100 - penalty`.
- **FACT OBJ-AGG**: The four scores are multiplied by their respective weights
  and summed. The theoretical maximum total is 100 points.

## Subproblems

- **Q1**: Under all PBS rules, build a scheduling model that makes the final
  assembly input sequence satisfy production preferences as much as possible.
  Apply it to Attachments 1 and 2, report scores, and write schedules to
  `result11.xlsx` and `result12.xlsx` in Attachment 4 format.
- **Q2**: Remove PBS constraints 6 and 7 only (MOVE-08 priority and MOVE-09
  first-arrival priority), keep all other constraints, build the model, apply
  it to Attachments 1 and 2, report scores, and write schedules to
  `result21.xlsx` and `result22.xlsx`.

## Attachment Mapping

- **FACT DATA-01**: Attachment 1 is normal de-identified production data.
- **FACT DATA-02**: Attachment 2 is adjusted data intended to test model and
  algorithm adaptability.
- **FACT DATA-03**: Attachment 3 supplies the region-code map: six inbound
  lane positions `[11..610]`, return positions `[71..710]`, paint-PBS exit
  `0`, receiving transfer machine `1`, delivery transfer machine `2`, and
  PBS-final-assembly receiving point `3`.
- **FACT DATA-04**: Attachment 4 is a blank 50-row by 100-second output
  template, not a solution.

## Explicit Ambiguities

- **AMBIGUOUS A-01**: The exact temporal overlap of lane propagation, machine
  travel, and zero-time load/unload is not specified. The adopted discrete
  epoch model is recorded as A-01 and will be used consistently for all four
  result files.
- **AMBIGUOUS A-02**: Objective 2 does not state whether "ratio 1:1" requires
  equal nonzero counts or allows `0:0`. The implementation treats an empty
  block as invalid and otherwise requires equal counts of 4WD and 2WD.
- **AMBIGUOUS A-03**: The statement calls lane position 1 the loading point
  and position 10 the unloading point; this is implemented exactly as written.
- **AMBIGUOUS A-04**: The statement does not define how long a vehicle remains
  in a region after a zero-time transition. The output uses a one-second
  occupancy cell and records the last region per STATE-02.
