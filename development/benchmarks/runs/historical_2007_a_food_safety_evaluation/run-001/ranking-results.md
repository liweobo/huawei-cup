# Ranking Results

## Claim boundary

The problem does not require a ranking. The following result is a fictional six-cell stress test of optional regulatory triage. It is not an assessment of any real region, contaminant, year, or standard.

## Formal primary triage

| Priority | Unit | Hard class | Point ratio | Upper ratio | Driver |
|---:|---|---|---:|---:|---|
| 1 | Coast-C | VIOLATION | 1.21 | 1.36 | point and upper ratios exceed one |
| 2 | North-A | VIOLATION | 1.20 | 1.35 | point and upper ratios exceed one |
| 3 | West-B | VIOLATION | 1.05 | 1.07 | point and upper ratios exceed one |
| 4 | South-A | UNCERTAIN | 0.95 | 1.10 | point below one, upper bound above one |
| 5 | East-B | COMPLIANT_UNDER_MODEL | 0.80 | 0.90 | upper ratio below one |
| 6 | Central-C | COMPLIANT_UNDER_MODEL | 0.60 | 0.75 | upper ratio below one |

`Coast-C` and `North-A` differ by only `0.01` in upper ratio. They are `NEAR_TIE_FOR_TRIAGE`; uncertainty could reverse them, so no materially meaningful winner claim is made.

## Baseline comparison

The hard-gated equal-weight/min-max baseline order is:

`North-A > West-B > Coast-C > South-A > East-B > Central-C`.

Against the primary order:

- Spearman rank correlation: `0.829`;
- top-three overlap: `1.00`;
- all hard classes: identical, because classification precedes scoring.

The complex/primary rule does not improve a predictive metric; it improves semantics by removing compensation at the compliance gate and making uncertainty the first within-class driver. The baseline's different first-place order is evidence against treating a compensatory score as the official recommendation.

## Score precision and interpretation

Baseline scores are reported in `outputs/ranking-results.json` for audit, with per-indicator contributions. They are not repeated to six decimals here because the choice of weights/normalization does not support such precision. They are `RELATIVE_COMPOSITE_SCORE`, not `ABSOLUTE_RISK_PROBABILITY` and not `REGULATORY_COMPLIANCE`.

The primary rule is lexicographic rather than additive. No invented “contribution percentage” is assigned to it; the driver is the first decisive hard/lexicographic field shown in the table.
