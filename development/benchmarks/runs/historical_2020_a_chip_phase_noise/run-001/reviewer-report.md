# Reviewer Report

Overall Status: NEEDS EVIDENCE

## P0 Critical

| ID | Evidence location | Issue | Impact | Minimal fix | Recheck |
|---|---|---|---|---|---|
| P0-2020A-01 | `problem-facts.md`, source DOCX | BER threshold is not stated in the extracted problem source | RSNR cost and feasibility are parameterized rather than uniquely determined | Supply the official BER threshold or define it as a benchmark parameter | Re-run all RSNR gates |

## P1 Serious

| ID | Evidence location | Issue | Impact | Minimal fix | Recheck |
|---|---|---|---|---|---|
| P1-2020A-01 | `outputs/channel_order_sensitivity.csv` | Channel order between dispersion and phase noise is not specified and shifts the result by about 0.5 dB | Q1-Q3 feasibility is model-order dependent | State the order or provide a channel block equation | Re-run with the official order |
| P1-2020A-02 | `skill/workflows/*`, run-local frequency audit | The frozen Skill has no explicit reusable FFT frequency, normalization, complex-power, or PSD/dB contract | Signal-processing conventions had to be created manually; omission could cause P0 unit/normalization errors in another run | Add a compact generic spectral-analysis contract to Skill after blind freeze review | Run a new blind signal-processing benchmark |
| P1-2020A-03 | `outputs/q3_candidates.csv` | No robust fixed-point candidate satisfies both the 0.3 dB gate and the 145 Gbaud payload constraint under the declared stress grid | Q3/Q4 cannot yield a valid minimum-resource design under this parameterization | Confirm BER threshold/order and widen the algorithm family only after the source contract is fixed | Repeat Q3/Q4 |

## P2 Important

| ID | Evidence location | Issue | Fix |
|---|---|---|---|
| P2-2020A-01 | `problem-facts.md` | Complex power notation in equations (2)-(3) is visually written as a square | Preserve the literal equation and state the `|.|^2` engineering interpretation |
| P2-2020A-02 | `source/rendered` | Standard DOCX page rendering could not run because `soffice.exe` is absent | Re-run visual page QA in an environment with LibreOffice |
| P2-2020A-03 | `outputs/q2_overhead_grid.csv` | Best-effort grid is non-monotone under one finite frame | Use multiple seeds or confidence intervals after the source contract is fixed |

## P3 Polish

| ID | Evidence location | Issue | Fix |
|---|---|---|---|
| P3-2020A-01 | figures | Figure source data and axes are present, but visual page QA of the DOCX source remains unavailable | Inspect figures and source pages in a full document environment |

## Required Evidence / Questions

- Official BER threshold and pre/post-FEC interpretation.
- Exact channel order and whether `D_z` is cumulative or per-km.
- Whether the intended signal model is one sample per symbol or oversampled.
- Whether the fixed-point resource proxy should be normalized per lane or for all 128 lanes.

## Fix Order

Must Fix: BER threshold and channel order before treating any RSNR number as unique.

Should Fix: add the generic spectral-analysis contract to Skill; repeat with multiple seeds and confidence intervals.

May Defer: document visual rendering and figure polish.
