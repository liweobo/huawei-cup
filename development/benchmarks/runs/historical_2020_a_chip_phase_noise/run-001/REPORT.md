# 2020A Fifth-Problem Blind Run

## 1. Source Provenance

The sole source was the official GitHub DOCX listed in `source/source-provenance.json`: URL, Git blob SHA `df90afc46266bc844cb03992baa5eb89c3e72555`, SHA256 `d2d2b7c5e9b3f2d03bbc63123f496b9e3058715c1cef046fca0dcd6b09686a94`. The original file was not modified. No 2020A excellent solution, code, blog, answer, or review was accessed.

## 2. Problem Facts

The DOCX contains four CR/ASIC design subproblems: minimum pilot overhead, linewidth-dispersion-pilot relationship, fixed-point/resource minimization, and a joint performance-resource objective. The exact equations and ambiguity flags are in `problem-facts.md`.

## 3. Signal Ledger

The run uses one complex sample per symbol at 150 Gbaud, normalized square 16QAM, cumulative Wiener phase noise, complex AWGN, known pilots, and a two-sided FFT frequency grid in Hz. See `signal-ledger.md`.

## 4. Sampling Audit

`F_s=150e9 Hz`, `dt=6.6666667 ps`, Nyquist interval `[-75,75) GHz`, frame length `N=32768`, observation duration `218.45 ns`, and FFT spacing `4.5776367 MHz`. No aliasing correction or zero-padding is claimed. The one-sample-per-symbol model is an explicit assumption because no oversampled data are supplied.

## 5. Frequency Convention

The dispersion transform uses `f=fftfreq(N,1/F_s)` in Hz and a two-sided complex DFT. Angular frequency is not passed to FFT APIs. Bin spacing is not described as physical resolution. No one-sided PSD conversion is used.

## 6. Amplitude / Power / PSD Definitions

The signal is normalized by `E|s|^2=1`. Complex AWGN is generated with total noise power `P_n` and per-component variance `P_n/2`. SNR is `10 log10(P_s/P_n)`; amplitude ratios are never converted with the power formula. No PSD, ASD, dBc, or dBc/Hz result is reported because the primary algorithm is a communication BER/RSNR simulation rather than a spectral-density estimator.

## 7. Preprocessing

The only transformations are pilot insertion, known dispersion/compensation, optional ADC and phase quantization, pilot phase extraction, unwrap, a width-3 moving average candidate, and interpolation. No detrending, resampling, arbitrary filtering, or cosmetic smoothing is used. Full provenance is in `preprocessing-record.md`.

## 8. Baseline

The AWGN-only normalized 16QAM reference reached `BER*=1e-2` at `13.8196 dB` under the recorded finite-frame/grid protocol.

## 9. Primary Algorithm

The primary candidate is known-pilot phase observation, unwrap, width-3 smoothing, linear interpolation, and complex phase rotation. A decision-directed residual tracker was tested as the third candidate. The exact contract is in `algorithm-contract.md`.

## 10. Parameter Choices

The main BER threshold is `1e-2`; `1e-3` is sensitivity only. The main channel ordering is dispersion then phase noise then AWGN, followed by inverse dispersion and CR. Pilot period, bit widths, resource scaling, and seed are explicit in `design-model.md` and `work/runtime-provenance.json`.

## 11. Synthetic Verification

All transform checks passed. Parseval and known-dispersion reconstruction are at machine precision, and phase unwrap recovers the known sequence. Details are in `work/synthetic_checks.json`.

## 12. Real Execution

There is no attached real measurement file in the official DOCX. The results are therefore reproducible synthetic communication frames, not measured chip data. Q1-Q4 code executed successfully after fixing one ordinary Gray-demapping bug and one JSON non-finite serialization bug; both fixes are recorded by the final code state.

## 13. Spectral / Numerical Stability

FFT normalization and inverse reconstruction are stable. Common-randomness comparisons were used across candidate periods. Q1 candidate ranking is still noisy under one finite frame, and the channel-order sensitivity is material. These limitations prevent a unique engineering optimum claim.

## 14. Validation

Q1 had no candidate below the `0.3 dB` gate. Q2 had zero passing grid points under the declared main protocol. Q3 had zero robust fixed-point candidates across the declared stress grid. Q4 therefore remains exploratory.

## 15. Error Analysis

The main sources of uncertainty are the missing BER threshold, missing channel order, ambiguous cumulative-dispersion units, one-sample-per-symbol assumption, finite-frame Monte Carlo variance, and proxy rather than synthesized resource counts. The alternate channel order changed coarse-grid RSNR thresholds by roughly `0.5 dB`.

## 16. Final Results

The best-effort Q1 design is width-3-smoothed linear interpolation, period `L=107`, overhead `0.9346%`, gate BER `0.012954`, and estimated RSNR cost `0.9826 dB`; it fails the requirement. At `BER*=1e-3`, the same protocol gives `1.6211 dB` cost. Q3/Q4 do not produce a valid resource-minimum solution.

## 17. Skill Strengths

The frozen Skill reliably routed the run through problem analysis, input audit, model design, baseline, experiment, validation, and reviewer stages. Its evidence rules correctly preserved failures, provenance, fixed seeds, and implementation-vs-method distinctions.

## 18. Skill Weaknesses

The frozen Skill has no explicit generic spectral-analysis contract for FFT frequency units, normalization, complex power, PSD/ASD, window/leakage, or frequency resolution. These had to be authored locally before the algorithm could be trusted.

## 19. First Meaningful Failure

The first implementation failure was an ordinary Gray-code demapping bug, caught by the AWGN sanity check and fixed before formal results. The first Skill-level failure was the absence of the reusable spectral contract described above; without the run-local audit, the Hz/rad/s and complex-power choices would have been implicit.

## 20. Failure Classification

Implementation bugs: fixed, no longer a result defect. Skill gap: `P1`, because the omission could become `P0` in another frequency-domain problem but was manually controlled here. Source-model under-specification: `P0/P1 evidence blocker` for a unique RSNR answer because threshold and channel order are missing.

## 21. Generalizable Gap Candidate

`GENERALIZABLE_SIGNAL_PROCESSING_GAP`: add a compact, domain-neutral contract requiring explicit sampling rate, FFT length/normalization, frequency-bin convention, one/two-sided choice, amplitude/power/PSD units, window/leakage handling, phase representation, and spectral-resolution limits. This is reusable beyond chip phase noise and does not require a DSP platform.

## 22. Remaining Uncertainty

The missing official BER threshold and channel order are unresolved. Visual page rendering of the DOCX is also unverified because `soffice.exe` is absent, although OOXML, formulas, images, and embedded objects were extracted and inspected.

## 23. Historical Integrity

The blind run did not access the 2020A excellent-paper directory. `skill/` was not modified. Historical 2011B, 2022C, 2023E, and 2024C assets were not modified. Pre-existing untracked 2022C files were preserved.

## 24. Final Decision

`BLIND_RUN_PARTIAL`. The run is complete as a reproducible, audited blind experiment, but the source does not uniquely determine the RSNR threshold or channel order and the declared main protocol has no feasible Q1-Q4 design. The top generalizable gap candidate is the missing reusable signal-processing contract; it must be reviewed after the blind freeze and is not fixed in this run.
