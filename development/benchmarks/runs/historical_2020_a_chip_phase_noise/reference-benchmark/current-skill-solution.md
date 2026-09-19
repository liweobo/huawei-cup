# Frozen Blind-Run Solution Summary

This file is a read-only summary of `run-001`, prepared before reading the five reference papers. It is not a replacement for the frozen run artifacts.

## Frozen status

- Run: `historical_2020_a_chip_phase_noise/run-001`
- Decision: `BLIND_RUN_PARTIAL`
- Skill modified during blind run: `false`
- Excellent solutions accessed before this summary: `false`
- Main BER gate: `1e-2`; sensitivity gate: `1e-3`
- AWGN baseline RSNR: about `13.8196 dB`

## Frozen numerical results

- Q1 best attempt: width-3 smoothing plus linear interpolation, `L=107`, pilot overhead `0.9346%`, BER `0.012954`, RSNR cost `0.9826 dB`; the `<0.3 dB` target was not met.
- Q2: zero passing points on the 28-point linewidth/dispersion grid.
- Q3: no robust feasible fixed-point candidate.
- Q4 exploratory point: `B_rx=6`, `B_phi=8`, `L=96`, payload `148.4375 Gbaud`, resource proxy `266395 U`, RSNR cost `3.8114 dB`.
- Channel-order sensitivity changed coarse-grid thresholds by about `0.5 dB`.

## Frozen interpretation and validation

The run preserved unresolved problem evidence instead of silently resolving it: the official BER threshold was not reliably extracted from the DOCX, dispersion/phase-noise order was not explicit, cumulative-dispersion units were ambiguous, and no real measurement data were supplied. The run used one sample per symbol with `Fs=150 GHz` as an explicit assumption, retained the assumption in the signal ledger, and documented Hz frequency bins, complex-power interpretation, phase unwrap checks, dispersion reconstruction checks, fixed seeds, and failed candidates.

## Frozen first failure

`Frozen Skill lacks a reusable spectral-analysis contract covering FFT frequency units, normalization, complex power, PSD/ASD, phase conventions, and resolution.`

The blind run classified this as `P1` and named the candidate `GENERALIZABLE_SIGNAL_PROCESSING_GAP`. This post-hoc benchmark may narrow or reject that name, but must not edit the frozen run or alter its numerical results.
