# Q1 Comparison

The results are not directly comparable to the frozen run because protocols differ in BER gate, frame length, pilot placement, sampling, and phase/dispersion treatment.

| reference | method | pilot result | RSNR / BER protocol | comparability |
|---|---|---|---|---|
| R1 | pilot phase de-spiking plus linear interpolation | gap 2900, overhead `~3.45e-4` | BER `0.02`, RSNR `<0.3 dB` | NOT_DIRECTLY_COMPARABLE |
| R2 | pilot averaging, LS/MAP-style phase estimation | overhead `3.13%` in abstract; table search varies | BER `0.02`, RSNR `<0.3 dB` | NOT_DIRECTLY_COMPARABLE |
| R3 | pilot block averaging plus interpolation | 9/826, `1.09%` | BER `0.02`, analytic AWGN baseline `12.71 dB` | NOT_DIRECTLY_COMPARABLE |
| R4 | two endpoint pilots, FFT window, linear interpolation and decoupling | `2/256 = 0.78125%` | BER `0.02`, RSNR `<0.3 dB` | NOT_DIRECTLY_COMPARABLE |
| R5 | CRAP1 pilot design and enumeration | `1/1024` in abstract | BER `0.02`, RSNR `<0.3 dB` | NOT_DIRECTLY_COMPARABLE |

Frozen run: width-3 smoothing plus linear interpolation, `L=107`, overhead `0.9346%`, BER `0.012954`, RSNR cost `0.9826 dB` at the blind-run gate. The reference spread itself demonstrates that algorithm quality cannot be judged from overhead alone without a protocol contract.
