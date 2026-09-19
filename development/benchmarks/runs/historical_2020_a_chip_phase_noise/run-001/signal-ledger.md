# Signal Ledger

| Signal | Meaning | Type | Sampling rate / interval | Count / duration | Units and amplitude definition | Time/frequency reference | Components and source |
|---|---|---|---|---|---|---|---|
| `s[k]` | transmitted 16QAM symbols | complex, discrete | `F_s=f_b=150e9 Hz`, `dt=1/F_s` | frame-specific; default `N=65536`, `T=N/F_s` | normalized average symbol power `E|s|^2=1`; pilots replace payload symbols | `k=0..N-1`; FFT frequency `f_m=fftfreq(N,dt)` in Hz | Gray-coded square 16QAM generated with a recorded seed |
| `dtheta[k]` | phase-noise increment | real, discrete | one increment per symbol | `N-1` | radians; zero mean, variance `2*pi*LW/f_b` after converting `LW` kHz to Hz | phase is accumulated from `theta[0]=0` | Wiener process from problem Eq. (7), synthetic seed |
| `theta[k]` | accumulated phase noise | real, discrete | same as symbols | `N` | radians; wrapped only for complex exponential, unwrapped for pilot interpolation | symbol-time reference | cumulative sum of `dtheta` |
| `x_disp[k]` | dispersed complex waveform | complex, discrete | same `F_s` | `N` | same normalized complex amplitude | circular block DFT/IDFT | `IFFT(FFT(s)*H(f))`, Eq. (8) interpretation |
| `r[k]` | received complex sample before CR | complex, discrete | same `F_s` | `N` | signal plus AWGN; optional fixed-point ADC quantization | positive/negative DFT bins retained internally | dispersion, phase noise, and AWGN channel |
| `p[k]` | known pilot symbols | complex, discrete | same `F_s` | `ceil(N/L)` for pilot period `L` | fixed normalized 16QAM corner `(3+3j)/sqrt(10)` | pilot positions `k mod L=0` | design choice, not supplied data |
| `phi_hat[k]` | estimated carrier phase | real, discrete | same `F_s` | `N` | radians; pilot phase is wrapped by `angle`, then unwrapped, optionally smoothed, then linearly interpolated | phase reference is known pilot phase | CR algorithm output |
| `f[m]` | FFT frequency grid | real, discrete | `df=F_s/N` | `N` bins | Hz; two-sided, ordered by `numpy.fft.fftfreq` | `m=0..N-1`, negative bins represented after `N/2` | used only for dispersion transfer function |
| `w[k]` | AWGN | complex, discrete | same `F_s` | `N` | `E|w|^2=P_s/SNR`; real/imag variance `P_n/2` | independent samples in the synthetic channel | generated from recorded seed |

## Frequency convention

All FFT calculations use Hz and a two-sided grid. No angular-frequency `omega` is passed to `fftfreq`; when the physical phase formula is evaluated, it uses the explicit `pi` factor and `f` in Hz. A one-sided PSD is never used in the primary algorithm. There is no zero padding: bin spacing is `df=F_s/N`, while actual resolution is limited by observation duration and the dispersion model/block assumptions.
