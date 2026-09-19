# External Knowledge Register

| Source | Claim used | Why needed | Confidence |
|---|---|---|---|
| NumPy FFT API, https://numpy.org/doc/stable/reference/generated/numpy.fft.fft.html | `fft` is the discrete Fourier transform under NumPy's documented normalization convention | define transform and inverse-transform normalization for dispersion simulation | high |
| NumPy frequency grid API, https://numpy.org/doc/stable/reference/generated/numpy.fft.fftfreq.html | `fftfreq(n,d)` returns cycles-per-unit frequency bins, including negative bins | prevent Hz/rad/s and bin-index mixing | high |
| NumPy unwrap API, https://numpy.org/doc/stable/reference/generated/numpy.unwrap.html | unwrap removes jumps larger than the chosen phase period using the documented discontinuity rule | define pilot phase handling | high |
| General digital communications convention | complex AWGN with total power `N0` has independent real/imaginary variance `N0/2` | simulate SNR and BER consistently | high |
| General square 16QAM convention | levels `{-3,-1,1,3}` normalized by `sqrt(10)` give unit average symbol power | construct a reproducible standard 16QAM frame | high |
| Problem DOCX Eq. (7) and Eq. (8) | linewidth phase increments and quadratic dispersion response | these are problem facts, not external solution material | high for text; unit interpretation separately marked |

No 2020A-specific paper, solution, code, blog, answer, or postmortem was accessed.
