# Q3 and Q4 Resource Comparison

| reference | fixed-point approach | resource accounting | Q4 objective |
|---|---|---|---|
| R1 | normalize complex samples; 10-bit representation; LUT arctan/trig; explicit phase wrap correction | analytic counts of adders, multipliers, LUTs, buffers | fitted cost versus bit width and pilot gap |
| R2 | variable bit width coupled to pilot length and payload throughput | timing pipeline and operation counts; no synthesis | RSNR/resource joint objective `J(G,F)` |
| R3 | 6-9 bit input widths; equivalent quantization-noise model | resource functions from arithmetic width and pilot count | resource minimum under RSNR and payload constraints |
| R4 | 3 integer bits plus 4 or 7 fractional bits; quantization-noise model | operation tables for FFT, LUT, buffer, multipliers | normalized weighted performance/resource objective and search |
| R5 | 6-9 bit widths; Taylor expansion for trig; feedback/automatic width | analytic U proxy and clock schedule | time/resource proxy per SNR improvement |

No paper reports ASIC synthesis, place-and-route, measured area, power, or timing closure. These are resource proxies based on assumed operation costs. The papers support retaining the frozen run's refusal to claim a robust Q3/Q4 feasible candidate when its own constraints were not met. They also show that fixed-point and resource modeling are 2020A-specific techniques, not the top generalizable signal-processing gap.
