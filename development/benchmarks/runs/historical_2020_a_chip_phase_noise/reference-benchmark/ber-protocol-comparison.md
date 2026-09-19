# BER and RSNR Protocol Comparison

| reference | threshold | classification | pre/post-FEC | baseline / RSNR protocol | reliability evidence |
|---|---:|---|---|---|---|
| R1 | `2e-2` | REFERENCE_ASSUMPTION | direct decision; no FEC in model | compare impaired and AWGN BER/SNR; pilot gap sweep | no confidence interval or stopping rule |
| R2 | `2e-2` | REFERENCE_ASSUMPTION | model includes FEC blocks in diagram, but reported BER is the communication-system decision metric | BER-SNR curves and RSNR difference | 1000 simulations mentioned; no interval reported |
| R3 | `0.02` | REFERENCE_ASSUMPTION | direct BER | analytic/Monte Carlo AWGN baseline, then impaired curve | `1e7` bits in code appendix, but no seed or uncertainty interval |
| R4 | `2e-2` | REFERENCE_ASSUMPTION | direct-decision interpretation | BER at fixed SNR and window/pilot sweeps | no error-count confidence interval; regression RMSE reported |
| R5 | `2e-2` | REFERENCE_ASSUMPTION | direct BER | RSNR cost from impaired versus no-linewidth baseline | code stops after `MAX_ERR_N=1000` errors, but no interval or seed |

The value `0.02` appears in all five papers, so it is a `REFERENCE_CONSENSUS` (`5/5`), not `EXPLICIT_FROM_PROBLEM` in this benchmark. The frozen run's `1e-2` main gate and `1e-3` sensitivity remain valid blind-run scenarios because the DOCX evidence was unresolved. The papers therefore support the decision to preserve the ambiguity; they do not authorize changing it.

All papers compare small numerical differences without reporting common random seeds, confidence intervals, or a clear minimum-error rule. This is a reference weakness and a possible secondary methodological issue, but it is not selected as the single top-1 gap because the blind-run failure was about signal formulation and can cause unit/scale errors across many signal domains.
