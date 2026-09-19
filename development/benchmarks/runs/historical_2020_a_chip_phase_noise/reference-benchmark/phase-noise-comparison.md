# Phase-Noise Model Comparison

All five papers use a discrete Wiener/random-walk construction in their main model. The common written form is `dtheta = sqrt(2*pi*LW/f_b) X_k` with `X_k ~ N(0,1)`, followed by cumulative summation. R1's appendix uses this square-root form explicitly; R2, R4, and R5 state the same relation in their equations; R3 derives the variance form through the cumulative phase-noise variance.

| reference | variance convention | phase handling |
|---|---|---|
| R1 | increment variance `2*pi*LW/f_b`; cumulative sum | pilot phase from ratio, spike removal, interpolation, unwrap-like continuity correction |
| R2 | Wiener process with variance proportional to elapsed sample count | pilot-block averaging and conditional-mean linear interpolation |
| R3 | cumulative variance proportional to `N*LW/f_b`; fitted pilot-phase variance `~0.015/M` | pilot averaging, interpolation choices compared |
| R4 | increment formula with `X~N(0,1)`, cumulative variance explicitly derived | phase ratio, LS/linear interpolation, frequency-shift decoupling |
| R5 | increment formula with `X~N(0,1)`, cumulative phase sum | phase from pilot ratio, angle/atan logic, linear interpolation |

The consensus is useful but not fully reproducible: some papers write linewidth in kHz in prose and Hz in formulas/code, and several do not state whether the phase is wrapped before interpolation. R1 and R5 explicitly correct phase branch discontinuities; R2/R3 use averaging/conditional interpolation; R4's endpoint method makes an implicit continuity assumption. This supports a lightweight phase-convention clause inside the broader spectral contract, not a separate 2020A-specific phase framework.
