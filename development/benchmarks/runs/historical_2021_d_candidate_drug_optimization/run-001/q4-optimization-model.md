# Q4 Optimization Model

Q4 is interpreted as a decision over the 50 compounds and descriptor rows supplied in the source test sheets. A descriptor is an observed attribute, not an independent design coordinate. No arbitrary 729-dimensional vector, SMILES reconstruction, chemical formula, or new structure is generated.

**Hard gates:** finite descriptor row; at least three predicted favorable ADMET classes; and pass under every target-specific applicability domain. The domain check uses the nearest training compound's RMS standardized distance over each final target-specific feature set, bounded by the training leave-one-out q95, plus zero selected-feature min/max violations.

**Objective:** among hard-feasible candidates, maximize `predicted pIC50 - 1 × outer-fold prediction SD`. The uncertainty coefficient is DERIVED and checked at 0 and 2. No ADMET probabilities are averaged into a fictitious joint probability. CYP3A4=1 is an explicit ASSUMED favorable direction; the opposite direction is a required sensitivity.

The search exhaustively evaluates all 50 fixed candidates, so `OPTIMAL` applies only to this finite surrogate ranking. It does not establish real activity, real ADMET, synthesis feasibility, or global molecular optimality. The synthetic check verifies that infeasible and out-of-domain high-score records cannot replace a feasible incumbent.
