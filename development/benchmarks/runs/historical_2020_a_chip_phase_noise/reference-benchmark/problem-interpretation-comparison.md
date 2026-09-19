# Problem Interpretation Comparison

All five papers cover all four tasks and identify the system as 16QAM carrier recovery with dispersion, phase noise, AWGN, pilot-assisted phase estimation, and ASIC resource constraints. Their results are reference interpretations, not official facts.

| paper | BER / RSNR interpretation | Q1 result | notable interpretation |
|---|---|---|---|
| R1 | Assumes BER `2E-2`, RSNR cost `0.3 dB`; cites the problem model and defines direct-decision BER | pilot gap 2900, overhead about `3.45e-4` | uses denoised pilot phase, linear interpolation, 10-bit fixed point |
| R2 | BER `2e-2`; RSNR is the difference between impaired and AWGN SNR at the gate | pilot overhead `3.13%` in abstract; later tables use frame/pilot searches | explicit OSR=8 pulse-shaping model, LS pilot averaging |
| R3 | BER `0.02`, analytic AWGN baseline about `12.71 dB` | 9 pilots / 826 symbols, `1.09%` | reduces phase-noise estimation to variance and pilot averaging |
| R4 | BER `2e-2`, RSNR cost `<0.3 dB` | two pilots per 256-symbol window, `2/256` | explicitly models dispersion/phase-noise decoupling and window length |
| R5 | BER `2e-2`, RSNR cost `<0.3 dB` | `1/1024` in abstract; tables use several frame/pilot cases | direct FFT/IFFT channel simulation and analytic resource proxy |

The papers disagree materially on algorithm family, frame length, pilot placement, and whether dispersion has a meaningful residual coupling. Those are technique choices or model assumptions, not evidence that the frozen run should be rewritten.
