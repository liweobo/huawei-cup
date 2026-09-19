# Generalizable Gaps

## Candidate assessment

| candidate | class | decision |
|---|---|---|
| `SPECTRAL_CONVENTION_AND_NORMALIZATION_CONTRACT` | G1 | selected |
| `SIGNAL_PROCESSING_PROVENANCE_CONTRACT` | G1/G4 overlap | useful sub-clause, but too broad for top-1 |
| `MONTE_CARLO_COMMUNICATION_VALIDATION` | G1 candidate | real secondary concern; not selected |
| `PHASE_ESTIMATION_VALIDATION` | G2/G1 overlap | important for this problem, narrower than evidence supports |
| PSD/ASD framework | G2/G4 | not activated globally; only when a task claims a density quantity |
| fixed-point/resource framework | G2 | 2020A-specific technique |

## Top-1 decision

`GENERALIZABLE_SIGNAL_PROCESSING_GAP_FOUND`

**gap_name:** `SPECTRAL_CONVENTION_AND_NORMALIZATION_CONTRACT`

**blind_run_evidence:** The frozen run had to write run-local rules for Hz versus FFT-bin indexing, `Fs=150 GHz` assumptions, complex power, phase wrapping, transform scaling, and frequency resolution. The frozen first failure explicitly names the absence of a reusable contract.

**reference_evidence:** All five papers use FFT/IFFT or frequency-domain quadratic phase, but generally omit at least one of sampling-rate declaration, negative-frequency ordering, DFT normalization, Parseval/power scaling, or phase branch convention. R2 and R5 even use different oversampling/FFT choices than the one-sample models. This makes numerical results non-reproducible across otherwise similar implementations.

**why generalizable:** The same failure can change units, amplitude/power, phase, or resolution in vibration, acoustics, radar, communications, sensors, and generic time-frequency analysis.

**why not 2020A-specific:** The contract concerns any sampled complex or real signal transformed into a frequency domain; it does not prescribe pilot recovery, 16QAM, linewidth, dispersion, or ASIC design.

**expected competition impact:** It prevents plausible-looking but dimensionally wrong spectra, incorrect power ratios, hidden aliasing, false resolution claims, and phase interpolation errors. It improves comparability without requiring a DSP library.

**minimal skill scope:** For each task-relevant transform, require a short record of `Fs`/`dt`, units and frequency grid, FFT length and normalization, window/zero-padding, one/two-sided mapping, complex power definition, phase convention, and resolution versus bin spacing. Activate PSD/ASD/dBc/Hz clauses only when those quantities are actually used. Add one synthetic regression for a known tone or reconstruction/Parseval identity.

**recommended next phase:** After human review, update the Skill once with this lightweight contract and synthetic regression. Do not modify the Skill in this post-hoc benchmark.
