# Channel Order Comparison

| reference | channel model / order | classification | evidence |
|---|---|---|---|
| R1 | dispersion by FFT/IFFT, then phase-noise multiplication, then AWGN; receiver dispersion compensation precedes CR | DISPERSION_THEN_PHASE | model text and MATLAB appendix |
| R2 | transmitter model lists dispersion -> phase noise -> AWGN; receiver performs dispersion compensation then phase estimation/compensation | DISPERSION_THEN_PHASE | system block diagram and Sections 3.2-3.4 |
| R3 | dispersion and phase-noise models are written sequentially; then pilot CR | DISPERSION_THEN_PHASE | Sections 5.1.4-5.1.5 |
| R4 | dispersion -> phase noise -> AWGN; receiver compensation order is dispersion then CR; explicitly derives residual coupling | DISPERSION_THEN_PHASE | Sections 4.3-4.5 and 5.2 |
| R5 | signal gets dispersion, phase noise, AWGN; receiver applies dispersion compensation then phase correction | DISPERSION_THEN_PHASE | Sections 3.1-3.3 |

There is a reference consensus on the operational order (`5/5`), but R1/R3/R5 simplify or effectively minimize coupling while R4 treats the non-commutation/coupling as central. This is `REFERENCE_CONSENSUS_ONLY`, not an official resolution of the original ambiguity. The frozen run's order sensitivity experiment and preserved assumptions were appropriate.
