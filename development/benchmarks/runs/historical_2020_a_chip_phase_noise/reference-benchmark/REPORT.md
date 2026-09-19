# 2020A Excellent-Solution Post-hoc Benchmark

## 1. Reference Set

Five PDFs were discovered in the permitted GitHub directory and all five were reviewed: R1 Fudan, R2 Shanghai Jiao Tong, R3 Huazhong University of Science and Technology, R4 Chongqing University, and R5 Army Engineering University. Full metadata and hashes are in `source-ledger.md`.

## 2. Source Reliability

All PDFs were valid, had matching listed byte sizes, valid PDF magic bytes, and complete text extraction with `pdfplumber` (40, 35, 40, 40, and 43 pages; all pages non-empty; no extraction errors). Representative title, model, result, and resource pages were rendered with Poppler and visually checked. The collection membership does not verify award rank, so all award levels are `UNKNOWN`.

## 3. Frozen Blind Run

`current-skill-solution.md` summarizes the frozen run before reference reading. The run remains unchanged and its decision remains `BLIND_RUN_PARTIAL`.

The frozen run recorded Git HEAD `96ac0c29cdb5e9de106d803e4c34705e7b0c507f` at start and end, and the unchanged `skill/` tree hash `0403f67a027da7c342eb6697ce740b08456c7efda7d5f53152548dc9dd1f4a19`. The post-hoc benchmark produced no tracked diff under `skill/` or `run-001`.

## 4-8. Problem, BER, Order, Phase, Dispersion

All papers use BER `0.02` and RSNR cost `0.3 dB`, but this is a `5/5 REFERENCE_CONSENSUS`, not an official DOCX resolution. All use operational order dispersion -> phase noise -> AWGN, with receiver dispersion compensation before CR, but R4 explicitly models residual coupling while other papers simplify it. Phase noise is a discrete Wiener/random walk with the common `sqrt(2*pi*LW/f_b)` increment scale. Dispersion uses a common quadratic phase and conjugate inverse, but frequency units, FFT indexing, and cumulative `Dz` units are not documented consistently. Detailed evidence is in the comparison files.

## 9-12. Sampling, Frequency, FFT, Power, Phase

The references demonstrate the candidate gap rather than eliminate it. FFT/IFFT is universal, yet bin ordering, negative frequencies, normalization, and Parseval scaling are mostly implicit. R2 uses OSR=8 and R5's appendix uses `nfft=512`, while other models are closer to one sample per symbol. Complex power is treated informally. PSD/ASD and dBc/Hz are not central to the Q1-Q4 protocol and should not be forced into every signal task.

## 13-16. Q1-Q4

Q1 overheads range from `~3.45e-4` to `1/1024`, `2/256`, `1.09%`, and `3.13%`, but none is directly comparable with the frozen `0.9346%` because protocols differ. Q2 conclusions range from strong linewidth/dispersion coupling to near independence of dispersion. Q3/Q4 papers give detailed fixed-point and analytic resource proxies, but no ASIC synthesis evidence. They are technique choices, not a general Skill contract.

## 17-18. Simulation Reliability and Comparability

The references use BER sweeps and Monte Carlo, but generally omit common seeds, confidence intervals, or a standardized stopping rule. This is a real secondary validation weakness. Numerical comparison is `NOT_DIRECTLY_COMPARABLE` unless phase-noise law, dispersion convention, channel order, BER gate, sampling model, and RSNR definition all match.

## 19-23. Consensus, Strengths, Weaknesses, Gaps

The frozen Skill solution has clear advantages: source provenance, ambiguity preservation, signal ledger, explicit Hz convention, complex-power disclosure, reconstruction/Parseval checks, phase unwrap synthetic check, fixed seed, retained failed candidates, and sensitivity analysis. The references are broader in algorithm and resource design but are weaker in reproducibility of transform conventions. The single G1 gap is `SPECTRAL_CONVENTION_AND_NORMALIZATION_CONTRACT`; the contract is lightweight, cross-domain, and synthetic-testable. PSD/ASD is conditional rather than global.

## 24-28. Source Ambiguity and Current Skill Level

- BER threshold: `REFERENCE_CONSENSUS_ONLY`
- Channel order: `REFERENCE_CONSENSUS_ONLY`
- D_z convention: `MIXED_REFERENCES`
- SIGNAL_FORMULATION: STRONG
- SAMPLING_DISCIPLINE: ADEQUATE
- SPECTRAL_CONVENTIONS: WEAK
- PHASE_HANDLING: ADEQUATE
- SIMULATION_VALIDATION: ADEQUATE
- RESOURCE_MODELING: STRONG
- SOLUTION_QUALITY: ADEQUATE
- OVERALL: `NEEDS_SIGNAL_PROCESSING_IMPROVEMENT`

## 29. Final Decision

`GENERALIZABLE_SIGNAL_PROCESSING_GAP_FOUND`

This report only diagnoses the gap. It does not modify `skill/`, does not alter `run-001`, and does not rerun Q1-Q4.

## 29. Repository Environment Notes

The existing `DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING` remains recorded. The known `.tmp/github-publish-checkout` module mismatch and the pre-existing 2022C unfinished marker were not modified in this benchmark. Reference PDFs, extraction text, rendered PNGs, and work files remain local and uncommitted.
