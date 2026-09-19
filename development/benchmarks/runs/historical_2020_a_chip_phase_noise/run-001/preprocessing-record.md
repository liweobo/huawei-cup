# Preprocessing and Provenance

| Step | Parameters | Why needed | Effect on signal | Effect on target metric |
|---|---|---|---|---|
| 16QAM normalization | levels `[-3,-1,1,3]/sqrt(10)` | make signal power exactly comparable across frames | `E|s|^2` is approximately 1 | fixes the SNR denominator |
| Pilot insertion | one known corner pilot every `L` symbols | create phase observations | replaces payload symbols at known indices | pilot positions are excluded from payload BER; overhead is `1/L` |
| Dispersion channel | `H(f)=exp(j*pi*lambda^2*D_z/c*f^2)`; circular FFT block | instantiate Eq. (8) | rotates each two-sided FFT bin | creates a controlled frequency-domain channel |
| Dispersion compensation | multiply by `conj(H(f))` before CR | follows the receiver order in the题面 | restores a dispersed block under the chosen ordering | excluded from resource score by题面 instruction |
| Phase-noise generation | cumulative Gaussian increments, `var=2*pi*LW/f_b` | instantiate Eq. (7) | multiplicative complex rotation | creates the CR target |
| AWGN injection | complex noise with target `SNR_dB` | define RSNR experiment | adds independent real/imag noise | determines BER and RSNR cost |
| Fixed-point quantization (Q3-Q4 only) | signed symmetric clip, `F=B-2` fractional bits for signal; phase uniform quantizer | model ASIC quantization | clips/rounds received samples and phase estimate | adds quantization-induced BER/RSNR cost |
| Pilot phase extraction | `angle(r_p*conj(p))` | compare received and known phase | produces wrapped phase observations | measurement noise affects CR |
| Phase unwrap | NumPy-style unwrap, default `pi` threshold | connect phase trajectory across wraps | produces unwrapped pilot phase | avoids artificial +/-2pi jumps |
| Pilot smoothing | moving average over 1 or 3 pilot samples, chosen before final run | reduce AWGN phase-estimate variance | changes phase trajectory estimate | sensitivity is reported; no arbitrary smoothing beyond candidates |
| Phase interpolation | linear between adjacent pilot estimates; zero-order hold baseline | estimate payload phase | creates `phi_hat[k]` | interpolation error drives RSNR cost |

No detrending, resampling, filtering, spectral window, amplitude normalization after channel, or cosmetic smoothing is used. The dispersion FFT is a model operation, not a PSD estimate.
