# Dispersion Model Comparison

Four papers expose essentially the same quadratic phase response, usually rendered as

`H(f) = exp(j * (lambda^2 * pi * Dz / c) * f^2)`

with compensation by `H*(f)`. R4 additionally uses a residual decoupling response of the form
`exp(j * (lambda^2*pi*Dz/c) * [f^2-(f-omega0)^2])`.

| reference | f convention | sign / compensation | Dz interpretation | assessment |
|---|---|---|---|---|
| R1 | frequency grid called `f`; code uses `fb/sigLen : fb/sigLen : fb` | positive channel phase, conjugate compensation | code converts `20000 ps/nm` to a scaled value; unit trail is incomplete | convention implicit |
| R2 | frequency-domain grid `f`; OSR=8 and `fs=8*fb` in model | positive channel phase, conjugate compensation | `ps/nm` in symbols; no full unit conversion shown | convention implicit |
| R3 | frequency point `f`, quadratic phase | positive response and inverse response | symbols report `s/m` after conversion | convention implicit |
| R4 | frequency `f` and an additional frequency shift `omega0` | channel and inverse response, plus decoupling | treats Dz as `ps/nm`; code uses a converted `dp_Dz` | convention partly explicit, units not fully audited |
| R5 | `f` in FFT model; code uses `fb/sigLen` grid | positive phase and conjugate response | symbols use `ps/nm`; code uses scaled `Dz` | convention implicit |

The sign pattern is consistent after interpreting channel versus inverse compensation, but the papers do not consistently document FFT ordering, negative frequencies, or the exact physical unit conversion. `D_z` is therefore `MIXED_REFERENCES` as a documentation outcome: formula family is common, unit convention is not sufficiently explicit to resolve the official ambiguity.
