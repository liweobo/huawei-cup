# Generalizable Gaps

## Candidate screening against the G1 test

A candidate is G1 only if all eight conditions in §38 hold: the Skill genuinely lacks it; the
blind run needed a run-local workaround; the reference comparison supports it; it generalizes
beyond inventory; it materially affects correctness; it is expressible as a lightweight rule or
contract; it can be synthetically tested; and it will not grow into a Monte Carlo platform.

| candidate | 1 Skill lacks | 2 run-local patch needed | 3 reference support | 4 non-inventory | 5 material | 6 lightweight | 7 testable | 8 not a platform | verdict |
|---|---|---|---|---|---|---|---|---|---|
| STOCHASTIC_INPUT_PROVENANCE_GATE | no | no | no | yes | yes | yes | yes | yes | not G1 |
| SERVICE_METRIC_DEFINITION_GATE | no | no | no | yes | moderate | yes | yes | yes | not G1 |
| STOCHASTIC_SIMULATION_EVIDENCE_CONTRACT | no | no | no | yes | yes | no | yes | no | not G1 |
| RANDOM_STREAM_AND_POLICY_COMPARISON_CONTRACT | no | no | no | yes | yes | yes | yes | borderline | not G1 |
| STEADY_STATE_AND_REGENERATIVE_VALIDATION | no | no | no | yes | moderate | yes | yes | yes | not G1 |
| NONE | - | - | - | - | - | - | - | - | selected |

## Why each candidate fails condition 1

Condition 1 is the decisive one. A candidate must be something the current Skill is actually
missing, not a practice the blind run already performed correctly. For every candidate above, the
blind run already did the thing the candidate would enforce, without any Skill change and without
a run-local workaround.

- STOCHASTIC_INPUT_PROVENANCE_GATE. The blind run labelled every random law `GIVEN`,
  `DERIVED`, `ESTIMATED`, `ASSUMED` or `SCENARIO` in `stochastic-ledger.md`, refused to promote a
  mean or range to a family, and preserved the `c4` unit conflict. The references split on the
  lead law (R1 Normal, R2 empirical after K-S, R3 Lorentzian), which is evidence that the blind
  run's discipline is better than the references, not evidence that the Skill lacks it. Condition
  1 fails; this is a `SKILL_STRENGTH`.

- SERVICE_METRIC_DEFINITION_GATE. The blind run defined stockout probability and fill rate
  separately and never merged them. No reference defines either, so there is no reference
  pressure that would justify adding a gate. Condition 1 fails; this is a `SKILL_STRENGTH`, and
  the absence in the references is a `REFERENCE_WEAKNESS` rather than a Skill gap.

- STOCHASTIC_SIMULATION_EVIDENCE_CONTRACT. The blind run already reports replications, standard
  errors, intervals, seeds, a replication unit of one complete trajectory, and horizon and
  replication convergence. No reference simulates at all, so the reference comparison provides no
  support for adding a contract. Condition 1 fails. It also fails condition 8: a standing
  simulation evidence contract would be the beginning of a Monte Carlo platform.

- RANDOM_STREAM_AND_POLICY_COMPARISON_CONTRACT. The blind run used a recorded RNG
  (`numpy.Generator(PCG64)` with a `SeedSequence` and a fixed seed), common random numbers, paired
  differences with intervals, and separated search draws from evaluation draws. The references are
  deterministic and never search stochastically, so there is again no reference support.
  Condition 1 fails; this is a `SKILL_STRENGTH`.

- STEADY_STATE_AND_REGENERATIVE_VALIDATION. The blind run established the renewal-reward basis,
  used no arbitrary burn-in because each arrival regenerates the state, and kept the Q5 finite
  horizon intact with no period deleted. No reference establishes a long-run rate; R2 computes the
  right object without arguing why. That is a `REFERENCE_WEAKNESS`, not a missing Skill capability.
  Condition 1 fails.

## The one defect found in this problem family is already closed

The only real runtime defect the 2005D work exposed was
`ORDERED_PROTOCOL_NORMALIZATION_FALSE_NEGATIVE`, where the protocol-change guard sorted every list
and so treated an ordered event protocol as an unordered collection. That was fixed and verified
in `ORDERED_PROTOCOL_NORMALIZATION_READY` (`fix: preserve protocol sequence order in provenance`,
commit `e5552b4`), with the targeted regression in `../run-002-protocol-order/`. Per §12 it is not
eligible to be selected again as the top stochastic gap, and it was a general contract bug rather
than a stochastic-modeling gap.

## What the comparison actually shows

Across the eleven comparison dimensions required by the task, the blind run is inside the
reference consensus on every structural element and ahead of the references on provenance,
uncertainty, timing, cost auditing and optimality qualification. In the other direction, the
references did not demonstrate a single technique for this problem that the Skill needed and
lacked. R2's K-S test is the most interesting reference method, and the blind run had already made
the same empirical choice, so matching R2 would add no new capability.

## Classification summary

| candidate | classification |
|---|---|
| STOCHASTIC_INPUT_PROVENANCE_GATE | G3 reference difference only, resolved in the blind run's favour |
| SERVICE_METRIC_DEFINITION_GATE | G3/G4 reference weakness, not a Skill gap |
| STOCHASTIC_SIMULATION_EVIDENCE_CONTRACT | G3, and would violate the no-platform constraint |
| RANDOM_STREAM_AND_POLICY_COMPARISON_CONTRACT | G3, already satisfied |
| STEADY_STATE_AND_REGENERATIVE_VALIDATION | G4 reference weakness, already satisfied |
| Inventory-specific constants, Lingo/Matlab optimisers, Lorentzian/Normal fits | G2 inventory-specific technique, not generalizable |

TOP-1 generalizable gap: `NONE`.
