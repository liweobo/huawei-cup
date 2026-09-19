# Q2 Comparison

All papers study linewidth, dispersion, and pilot overhead, but the estimated relationships differ:

- R1 fits BER surfaces in linewidth, dispersion, and pilot gap and reports a coupling effect; large linewidth and dispersion can make the gate infeasible.
- R2 reports a mostly linewidth-driven relationship and claims dispersion has little effect over much of the range.
- R3 derives an approximate linear pilot-overhead/linewidth relation and treats dispersion through a simplified variance model.
- R4 reports a weak dispersion coefficient and a non-monotone window effect at high linewidth; it explicitly states that its simplification ignores some coupling.
- R5 reports step-like pilot overhead regions and a sharp growth region at high linewidth/dispersion.

These are not a single scaling law. They are consequences of different frame lengths, pilot estimators, sampling models, and coupling assumptions. The frozen run's zero passing points on its own 28-point grid therefore cannot be “corrected” by selecting one paper's fit after the fact.
