# CYP3A4 Semantics Comparison

## Favorable-direction ledger

| solution | favorable label | stated rationale/source | provenance classification | confidence |
|---|---:|---|---|---|
| Frozen `run-001` primary | `1` | unresolved source direction; evaluated as an explicit primary assumption | `ASSUMED`, sensitivity-tested | high |
| Frozen `run-001` reversal | `0` | deliberate direction reversal | `SENSITIVITY_CASE` | high |
| R1 | `1` | used in Q4 desirability encoding without a traceable source quotation | `UNSTATED` / `AUTHOR_ASSUMPTION` | high for mapping, low for basis |
| R2 | `0` | pattern `10010`; attributed generally to the problem without a source quotation or external definition | `AUTHOR_ASSUMPTION` | high for mapping, low for basis |
| R3 | `1` | states Caco-2/CYP3A4/HOB=`1` are favorable | `AUTHOR_ASSUMPTION` | high for mapping, low for basis |
| R4 | `0` | reasons that CYP3A4=`1` means the compound can be metabolized and fast metabolism is undesirable | `DOMAIN_INTERPRETATION` / `AUTHOR_ASSUMPTION` | high for mapping, medium for rationale |
| R5 | `1` | treats metabolizability as favorable | `AUTHOR_ASSUMPTION` | high for mapping, medium for rationale |

## Consensus test

- Favorable `1`: 3 of 5 references.
- Favorable `0`: 2 of 5 references.
- Reliable official source quotation: 0 of 5.
- Reliable cited external pharmacology definition that maps this dataset's label to the decision: 0 of 5.

There is no direction consensus, and even unanimous reference agreement would remain `REFERENCE_CONSENSUS`, not a source fact. The papers expose the same semantic ambiguity and resolve it through incompatible author choices.

## Effect on the frozen decision

The frozen run already performs the required sensitivity analysis: the primary assumption yields `TEST026`, the reversed assumption yields `TEST019`, and the unconditional recommendation remains `WITHHELD`. No historical data corruption or software defect is revealed. The ambiguity is `G6 SOURCE / SEMANTIC AMBIGUITY`, not `G1`.
