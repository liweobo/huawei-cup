# Surrogate and Claim Comparison

## Predictive model to real-world claim

| solution | explicitly bounded as surrogate | structure/experiment verification | claim assessment |
|---|---|---|---|
| Frozen `run-001` | yes | none claimed | conditional surrogate ranking only; efficacy and safety not claimed |
| R1 | not consistently | absent | descriptor optimization and improved predicted pIC50 are sometimes described as drug optimization; `REFERENCE_SURROGATE_CLAIM_OVERREACH` |
| R2 | not consistently | absent | predicted descriptor vector is called an optimal scheme despite arbitrary score provenance; overreach |
| R3 | partial | absent | limitations acknowledge local optimum and descriptor dependence; still no real molecule verification |
| R4 | not consistently | absent | descriptor ranges are linked to optimizing/synthesizing a drug without structural proof; overreach |
| R5 | not consistently | absent | claimed global/best drug optimization exceeds heuristic and descriptor evidence; overreach |

## Required boundary

A high predicted pIC50 plus predicted ADMET labels is evidence about fitted models. It is not experimental potency, safety, bioavailability, or clinical success. None of the references generates and validates a molecular structure, and none validates a proposed compound experimentally.

The frozen run keeps each promotion step explicit:

1. fitted prediction models;
2. finite candidate evaluation;
3. hard feasibility and empirical applicability gates;
4. uncertainty-adjusted surrogate ranking;
5. conditional recommendation under CYP3A4 semantics;
6. no claim of drug discovery or experimental performance.

## Finding

The reference set strengthens the need for the existing claim-boundary discipline. It does not expose a missing capability. `CLAIM_BOUNDARY` is rated `STRONG`.
