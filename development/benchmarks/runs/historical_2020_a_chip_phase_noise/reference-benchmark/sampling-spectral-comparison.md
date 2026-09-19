# Sampling, Frequency, FFT, and Power Comparison

| reference | sampling model | FFT / frequency convention | normalization / power | phase / resolution |
|---|---|---|---|---|
| R1 | one symbol per sample in the main model; `fb=150e9`; no explicit negative-frequency grid | FFT/IFFT used; bin grid and normalization not stated | uses magnitude/power in SNR discussion; no Parseval check | pilot gap is the practical resolution parameter |
| R2 | explicit OSR=8 pulse shaping and matched filtering, then downsampling | FFT/IFFT and `fs=8*fb` described, but bin ordering/normalization omitted | SNR uses power ratios; exact FFT scale not specified | frame length and pilot block determine interpolation scale |
| R3 | discrete symbols at baud-rate sampling | FFT/IFFT used for dispersion; grid details not reproducible | defines `|s|^2`/noise power in prose, but formula extraction is incomplete | no explicit spectral resolution analysis |
| R4 | window length `l`, often powers of two; code comments use `N_fft=128` | FFT/IFFT used with `f_b/N_fft` frequency grid | resource model counts FFT operations; no transform normalization or Parseval validation | window length is treated as both computational and estimation parameter |
| R5 | `fb=150e9`; code uses `nfft=512`, `osf=8` in appendix | FFT/IFFT and quadratic frequency response; bin indexing is code-dependent | SNR/RSNR uses energy-like sums; no explicit DFT normalization or Parseval test | no main-lobe/bin-resolution distinction |

Across the set, frequency is usually named `f` in Hz-like units, but negative frequencies and two-sided ordering are not consistently declared. FFT normalization is absent or only implicit in MATLAB defaults. Complex power is usually handled engineering-wise through magnitude or real/imaginary products, but no paper gives a reusable `conj(x)*x` contract. PSD/ASD and dBc/Hz are not required by the main solution protocol; the papers mostly use waveform simulation, BER, and RSNR. Therefore the general contract should activate PSD/ASD only when a task actually claims a density quantity.
