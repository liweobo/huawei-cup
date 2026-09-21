# Normalization Contract

## Primary model

No cross-alternative normalization is used for the formal compliance result. Physical quantities are converted to common units, and the dimensionless hard-gate ratio is `ρ=q/T`. Its reference is a fixed applicable authority threshold, not the current candidate set.

- **method:** physical unit conversion followed by threshold ratio;
- **formula:** `ρ=q/T`, `ρ_U=q_U/T`;
- **direction handling:** larger ratios are worse; threshold is one;
- **zero handling:** `T≤0` is invalid; nondetects enter a censored likelihood and are never zero-filled in the primary model;
- **outlier handling:** verify lab/unit/context; no automatic deletion;
- **range source:** regulatory/authority threshold with verified scope;
- **scope:** fixed external benchmark when operational, explicit assumed threshold only in synthetic runs.

Changing µg to mg multiplies both `q` and `T` by the same factor and leaves `ρ`, class, and rank unchanged.

## Equal-weight baseline

For criterion `x_j` among the current alternatives:

- benefit: `z_ij=(x_ij-min_i x_ij)/(max_i x_ij-min_i x_ij)`;
- cost: `z_ij=(max_i x_ij-x_ij)/(max_i x_ij-min_i x_ij)`;
- constant column: set all `z_ij=1`, contributing no discrimination;
- score: `S_i=Σ_j w_j z_ij`, higher meaning relatively safer/lower priority within the hard class.

This is `current alternatives` normalization. Adding/deleting an alternative can change every `z_ij`; the score is relative. The hard class is computed before the score and is unaffected by min-max ranges.

No missing value is filled with zero. A missing criterion blocks the score or triggers an explicitly scoped imputation sensitivity. Extreme values can stretch min-max ranges, so influence is audited.

## Sensitivity alternatives

1. **Fixed bounds:** point ratio `[0,1.5]`, upper ratio `[0,1.6]`, population `[0,60]`, coverage `[0,1]`; these are synthetic benchmark bounds, not policy standards.
2. **Vector normalization:** `x/||x||₂`, complemented for cost criteria. It is scale-invariant but candidate-set dependent.

All three produced the same synthetic baseline order and top-three set. This does not make min-max an absolute scale; it only shows stability for the declared scenario.
