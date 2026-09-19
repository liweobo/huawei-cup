# Validation Report

The run uses a fixed seed (`202009`), a common symbol frame and common channel noise across candidate periods, and `N=32768` complex symbols. The primary metric is payload BER at a fixed SNR gate equal to the AWGN reference RSNR plus 0.3 dB. A candidate passes only when BER is at most `1e-2`. RSNR thresholds are also estimated on a 0.5 dB grid with log-BER interpolation.

Synthetic checks passed: single-tone frequency error was 11.71875 MHz against a 36.62109375 MHz FFT bin spacing; Parseval relative error was zero to reported precision; phase unwrap RMSE was `1.29e-16 rad`; known dispersion inverse reconstruction maximum error was `2.43e-15`.

The AWGN reference RSNR was `13.8196 dB` for `BER*=1e-2`. Under the primary `dispersion_then_phase` ordering, the best Q1 candidate was width-3-smoothed linear interpolation with period 107, pilot overhead `0.9346%`, gate BER `0.012954`, and estimated RSNR cost `0.9826 dB`; it therefore failed the required `<0.3 dB` gate. The sensitivity run at `BER*=1e-3` gave reference `16.4805 dB`, CR `18.1017 dB`, and cost `1.6211 dB` for the same best-effort design.

For Q2, all 28 linewidth-by-dispersion grid points failed the strict gate. Best-effort results are retained in `outputs/q2_overhead_grid.csv`; for example, the best BER at `LW=10 kHz, D_z=0` was `0.010162` with period 2, while `LW=10 MHz, D_z=10,000 ps/nm` had best BER `0.127999` even at the tested periods. These values are diagnostics, not feasible solutions.

For Q3, no candidate across `B_rx in {6,7,8,9}`, `B_phi in {6,8,10}`, periods `{31,32,40,48,64,80,96,128}`, and the 12 stress scenarios passed the robust gate. Every tested period satisfied the payload throughput condition when `L>=31`; the failure was BER/RSNR, not throughput. The resource proxy is therefore a comparison tool only, not a valid minimum-resource answer.

For Q4, the representative scenario `LW=1 MHz, D_z=10,000 ps/nm` selected an exploratory best-effort point at `B_rx=6`, `B_phi=8`, `L=96`, payload `148.4375 Gbaud`, resource proxy `266395 U`, and RSNR cost `3.8114 dB`. Because it fails the performance gate and the robust Q3 search has no feasible incumbent, this is not reported as a valid design.

Numerical stability was checked over the synthetic transform identities, fixed-point widths, smoothing choices, pilot periods, and a common-randomness rerun. The decisive limitation is model-order sensitivity: with the same seed and parameters, changing the channel to `phase_then_dispersion` lowered the coarse-grid threshold by about `0.5 dB` for periods 2-64. The original DOCX does not state the order, so the result remains parameterized.
