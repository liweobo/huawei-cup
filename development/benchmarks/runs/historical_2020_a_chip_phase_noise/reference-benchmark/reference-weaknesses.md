# Reference Weaknesses

- FFT normalization, negative-frequency ordering, and exact frequency-bin definitions are usually absent.
- Sampling rate and one/two-sided conventions are inconsistent or hidden in MATLAB code.
- Complex power is used through engineering magnitude operations but is rarely stated as `conj(x)*x`.
- Phase wrap/unwrap continuity is inconsistently justified.
- BER estimates lack seeds, confidence intervals, or a common error-count stopping policy.
- Several reported numerical comparisons use different gates, frame lengths, and channel assumptions.
- Fixed-point resource claims are analytic proxies, not ASIC synthesis evidence.
- Q4 weights and normalizations are usually selected by the paper, not derived from an official specification.
- PSD/ASD and dBc/Hz are not central to the reported communication simulations, despite occasional power-spectrum plots.

These weaknesses are evidence about reproducibility and rigor, not proof that every reference result is incorrect.
