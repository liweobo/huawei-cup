# Reference Consensus

| topic | consensus | count | confidence | official status |
|---|---|---:|---|---|
| BER threshold | `0.02` | 5/5 | high as reference consensus | not official; source remains unresolved in DOCX extraction |
| channel order | dispersion -> phase noise -> AWGN; receiver dispersion compensation before CR | 5/5 | high | reference consensus only |
| phase-noise law | discrete Wiener/random walk; increment scale `sqrt(2*pi*LW/f_b)` or equivalent variance | 5/5 | high | model consensus, not an official clarification |
| dispersion formula | quadratic phase with conjugate inverse | 4-5/5 | medium-high | signs reconcile as channel/inverse pair; units remain underdocumented |
| sampling | one-sample baud-rate models common; R2/R5 include OSR/FFT variants | 3/5 simple, 2/5 oversampled | medium | not resolved |
| FFT convention | FFT/IFFT used | 5/5 | high | normalization/bin ordering mostly implicit |
| pilot strategy | pilot-assisted phase estimation | 5/5 | high | algorithm family consensus only |
| interpolation | linear, nearest, conditional mean, or fitted variants | mixed | medium | no universal method |
| fixed point | explicit width/quantization in Q3/Q4 | 5/5 | high | analytic resource proxies only |
| resource accounting | operation counts, LUT/buffer assumptions, timing schedules | 5/5 | high | no ASIC synthesis evidence |
| Monte Carlo protocol | random simulation / BER sweeps | 5/5 | high | seeds and uncertainty usually absent |

The strongest shared evidence supports a lightweight formulation/spectral contract. It does not support adding a PSD/ASD framework to every task or selecting a single paper's pilot algorithm as the skill requirement.
