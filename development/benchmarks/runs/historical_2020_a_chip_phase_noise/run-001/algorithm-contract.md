# Algorithm Contract

## Input

- `f_b=150e9 Hz`, complex 16QAM symbol frame, `LW`, cumulative `D_z`, pilot period `L`.
- Optional fixed-point widths `B_rx` and `B_phi` for Q3-Q4.
- A fixed random seed and frame length for reproducibility.

## Output

- Payload BER at each SNR.
- AWGN-only reference RSNR, CR RSNR, and RSNR cost in dB.
- Pilot overhead `1/L`, payload throughput `f_b*(1-1/L)`.
- Resource score in normalized U units and the operation/latency breakdown.

## Mathematical definition

1. Generate normalized Gray 16QAM `s[k]` and replace `k mod L=0` with known `p`.
2. Form `x_d = IFFT(FFT(s) H(f))`, where `H(f)` is the Eq. (8) interpretation recorded in `problem-facts.md`.
3. Form `r = x_d exp(j theta) + w`, with Eq. (7) phase increments and complex AWGN.
4. Apply the known inverse dispersion `IFFT(FFT(r) conj(H(f)))`.
5. At pilots, calculate `z_p = angle(r_p conj(p))`; unwrap across pilot index; optionally apply a width-3 moving average.
6. Interpolate pilot phases linearly. The third candidate then uses hard 16QAM decisions and a fixed `alpha=0.90` first-order accumulator on the residual phase error.
7. Compensate `y[k] = r[k] exp(-j phi_hat[k])` and make nearest-neighbor 16QAM decisions.

## ASIC mapping

- Pilot phase `angle` is represented by a LUT; the problem's resource rule for an `M-N` LUT is `2^M*N` up to the table-1 scaling constant.
- Complex multiply is four real multipliers and two adders; subtraction is counted as an add plus sign inversion as stated in the题面.
- Linear interpolation uses an add/subtract path and a multiplier; multiplication by powers of two is a shift and is free under the题面 convention.
- A phase/data alignment buffer is included for the maximum CR latency. Dispersion compensation and BER decision complexity are excluded as required.
- One clock supports at most one multiplier, four adders, and one LUT level; parallelism is 128 lanes.

## Failure conditions

- Missing or ambiguous BER threshold: results remain parameterized.
- `L < 31` in Q3-Q4: payload throughput is not greater than 145 Gbaud and the candidate is rejected.
- A phase estimate with unresolved wrap jumps, invalid NaNs, or a BER simulation with too few payload bits: candidate is rejected.

## Complexity

Per symbol, the primary CR path is constant-time: pilot phase observation only at pilots, one interpolation update, and one complex phase-rotation multiply. Frame-level dispersion compensation is `O(N log N)` but excluded from the ASIC score by the problem statement. Resource score is an explicit normalized proxy, not a synthesis result.
