# Validation-protocol comparison

## Q4

| ID | Final Q4 protocol | Multiple historical origins | Naive baseline | Same origins/targets | Per-horizon future error |
|---|---|---|---|---|---|
| Frozen | ROLLING_ORIGIN | YES | persistence | YES | YES |
| R1 | IN_SAMPLE_FIT / NO_VALIDATION | NO | NO | not applicable | NO |
| R2 | IN_SAMPLE_FIT / NO_VALIDATION | NO | NO | not applicable | NO |
| R3 | IN_SAMPLE_FIT / NO_VALIDATION | NO | NO | not applicable | NO |
| R4 | IN_SAMPLE_FIT / NO_VALIDATION | NO | NO | models disagree without controlled future truth | NO |
| R5 | historical augmented split; long crossing NO_VALIDATION | NO for intended issuance | NO | not demonstrated | NO |
| R6 | IN_SAMPLE_FIT / NO_VALIDATION | NO | NO | not applicable | NO |

## Same-time estimation

- Q1: all six use training-fit statistics, selection reuse or combined-sample reuse. None supplies future forecasting validation.
- Q2: R1/R2/R6 explicitly randomize at least part of their image split; R4 reuses training data for testing; R3/R5 do not disclose enough ordering/group information. These results concern same-time estimation, so they are not automatically future leakage. They provide weak event/time generalization evidence.
- Numerical model comparisons within several papers mix target definitions, fitted samples, derived series or unreported splits. They are not controlled comparisons with the frozen protocol.

The frozen run's Ridge loss to persistence remains unchanged. Reference algorithm complexity and fit quality do not replace evaluation on the same origins, horizons, targets and metric.
