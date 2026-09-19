# Validation Comparison

Common validation evidence in the references consists of BER/SNR curves, constellation plots, phase-noise traces, fitted surfaces, and operation-count tables. None provides independent measured data. R3 reports analytic/Monte Carlo consistency and R5 stops after a stated error count in code, but neither reports confidence intervals or common seeds. R4 compares extracted and generated phase traces, while R1/R2 emphasize sensitivity sweeps.

The frozen run is stronger in several run-local controls: fixed seed, synthetic phase unwrap check, dispersion reconstruction check, Parseval/reconstruction where applicable, explicit failed-candidate retention, and sensitivity to BER threshold and channel order. These are `SKILL ADVANTAGE` findings relative to the references. The references are stronger in breadth of algorithm and hardware design exploration, but breadth alone is not a validation contract.
