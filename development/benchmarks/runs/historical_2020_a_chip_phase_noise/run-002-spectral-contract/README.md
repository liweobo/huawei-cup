# 2020A Targeted Spectral Contract Regression

This is a post-fix, read-only regression for the frozen `run-001`. It checks
the new generic spectral convention capability against the frequency-domain
evidence already recorded by the blind run. It does not rerun or retune Q1-Q4.

The instantiation uses the executed runtime values `Fs=150e9 Hz` and
`N=32768`, NumPy's default unscaled-forward / `1/N`-inverse convention, a
two-sided `numpy.fft.fftfreq` grid, `|x|^2` complex power, no window, and no
zero padding. PSD/ASD is inactive. The official BER threshold remains
unresolved, channel order remains reference-consensus-only, and the dispersion
convention remains mixed across references; those source facts are not changed
by this contract regression.

Run with:

```text
python -B run_regression.py
```

The script writes `results.json` in this directory and reads only frozen
`run-001` and `reference-benchmark` evidence plus the Skill helper.
