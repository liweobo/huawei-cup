# Design Model and Blind-Run Assumptions

## Baseline

The minimum legal baseline is an AWGN-only 16QAM reference with perfect known dispersion compensation and no phase noise. Its RSNR is the SNR at which the chosen BER target is first reached.

For CR comparison, the simple baseline is one known pilot every `L` symbols, a wrapped phase observation at each pilot, unwrap, zero-order hold, and exact floating-point compensation.

## Candidate set

The blind run compares only three materially different candidates:

1. linear interpolation between adjacent pilot phases;
2. linear interpolation after a width-3 moving average of pilot phase;
3. linear interpolation followed by a one-tap decision-directed residual tracker with fixed `alpha=0.90`.

The primary candidate is selected by the smallest pilot overhead that passes the RSNR gate, then by lower resource score when quantization is enabled. No 2020A-specific algorithm was preselected.

## Assumptions requiring sensitivity

- The BER threshold is not supplied. Main run: `1e-2`; sensitivity: `1e-3`.
- The Eq. (8) OMML is used as `exp(j*pi*lambda^2*D_z/c*f^2)` with cumulative `D_z` in ps/nm.
- Channel order is dispersion, then phase noise, then AWGN; receiver compensation is inverse dispersion, then CR. Reversing the order is an additional mechanism sensitivity because it can remove much of the dispersion/phase interaction.
- A pilot is a normalized 16QAM corner symbol; one pilot every `L` symbols gives overhead `1/L`.
- One sample per symbol is used: `F_s=150 GSa/s`, Nyquist interval `[-75,75) GHz`. There is no oversampling data in the題面.
- The same parallelism `P=128` is used for the resource proxy in Q3-Q4.
- Fixed-point signal scaling is signed with `F=B_rx-2` fractional bits; phase quantization is uniform over `[-pi,pi)`.
- Resource weights follow table 1 by scaling 8+8 add = 1 U, 8x8 multiply = 8 U, 8-8 LUT = 128 U, and 8-bit 2048-symbol delay = 1 U.

## Validation plan

- Synthetic transform checks: single tone, two tones, white-noise Parseval, and phase unwrap with a known sequence.
- Communication checks: AWGN-only reference, repeated seeds, BER/RSNR threshold search, and Q1/Q2/Q3/Q4 sensitivity.
- Numerical stability: frame length, pilot interval, smoothing width, fixed-point widths, and phase-noise seed.
