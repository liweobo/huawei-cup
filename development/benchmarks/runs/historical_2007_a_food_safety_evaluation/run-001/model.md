# Model

## System architecture

The proposed assurance system is a traceable chain:

`sampling frames → intake model + contamination model → taxonomy/unit bridge → exposure distribution → uncertainty → hard compliance gate → warning/triage`.

Each output is indexed by population `g`, geography `r`, season/time `t`, food group `j`, and contaminant `c`. The same keys are stored with raw data so national, regional, and food-specific claims cannot be mixed silently.

## Population food-intake model

Use a stratified multistage probability sample rather than a convenience sample. Strata cover the dimensions explicitly named by the source when feasible: region, urban/rural setting, season, sex, age, labour intensity, and economic group. Let household `h` have inclusion probability `π_h`; its design weight is `d_h=1/π_h`. Calibration/post-stratification changes `d_h` to `w_h` so known population margins are reproduced without pretending the survey is a census.

For food group `j`, household stock-change consumption over `Δt` days is

`H_hj = stock_before_hj + purchases_hj - stock_after_hj - waste_hj ± transfers_hj`.

Unweighed foods are recorded through a declared auxiliary method. Household consumption is allocated to persons using observed meals/person-days or scenario shares; the allocation rule is part of uncertainty, not a hidden constant. Weighted empirical distributions or a hierarchical positive model give `F_I(i | g,r,t,j)`. Means/totals use the actual survey design and cluster/stratum bootstrap.

Food classification is driven by both consumption and contaminant profiles. Rare categories with materially different contaminant behavior are not merged merely to save work; similar categories can be pooled with hierarchical partial pooling. Multiple resolutions may coexist: a fieldwork taxonomy, canonical risk taxonomy, and reporting taxonomy.

## Contaminant distribution with nondetects

For observation `k` in a food-contaminant stratum, let concentration be `C_k≥0`, detection limit `L_k`, sampling weight `v_k`, and detection indicator `δ_k`.

For parametric distribution `F(·;θ)` with density `f`, the weighted left-censored log-likelihood is

`ℓ(θ)=Σ_k v_k [δ_k log f(C_k;θ) + (1-δ_k) log F(L_k;θ)]`.

Thus a nondetect contributes `P(C≤L)`, not a numeric zero. Quantified monitoring results contribute density terms. Qualitative compliance tests, monitoring tests, spot checks, circulation volumes, and ports retain separate method/provenance fields. If sampling was risk-targeted rather than probability-based, design weights or a selection model are required before population claims.

The runnable scenario uses a lognormal family and an EM fit to censored log concentration. An operational run compares a small set of defensible families or a semiparametric body-plus-tail model, checks probability plots and held-out/weighted diagnostics, and retains model-form sensitivity. The source's skew wording does not fix the family.

## Taxonomy reconciliation

Let `x` be quantities in a source taxonomy and `A` a nonnegative crosswalk to canonical groups. The mapped quantity is `x*=Aᵀx`, with each source row satisfying `Σ_j A_sj=1`. This mass-conservation condition detects dropped/double-counted categories.

Known one-to-one mappings use fixed `A`. Ambiguous mappings use bounded/scenario shares and propagate them through exposure. Historical categories are never rewritten in place; raw labels and crosswalk version remain available. This is also the guard against double weighting a category in mapping and again in aggregation.

## Joining unpaired samples

The intake survey and food monitoring survey do not identify the same people or foods. Under the declared conditional-independence assumption,

`I ⟂ C | (region, season, canonical food group, declared covariates)`.

Draw `I` and `C` independently only inside these shared strata, then aggregate using target-population weights. If both data sources do not support a requested stratum, partial pooling or transport weights may be used, but the claim scope shrinks and a dependence scenario is mandatory. Positive dependence between high consumption and high contamination is a conservative stress case; independence is not a universal fact.

## Regional-to-national transport

Let `s` be sampled regions and `r` target regions. A national estimator uses verified target shares `P(r)` and region-specific exposure models. When some `r` are absent, a hierarchical model borrows strength through measured region covariates and reports transport uncertainty. A selected set of similar provinces is not automatically a random national sample. Sensitivity varies pooling strength and excludes each source region in turn.

## Exposure and risk

For a person-day and contaminant `c`,

`D_c = Σ_j I_j C_jc`.

If the authority standard is body-weight normalized, use `D_c/W` and match the standard unit. Dependence across foods and contaminants is represented by a joint/copula/resampling structure when data support it; otherwise scenario bounds accompany the independence model.

Estimate `q_c=Q_0.99999(D_c)`. A direct Monte Carlo order statistic at such an extreme probability is unstable unless the simulation size and tail method are adequate. The operational route is:

1. fit the intake and censored contamination bodies with design weights;
2. select/validate a tail threshold using diagnostics rather than a convenient fixed percentile;
3. fit or simulate the upper tail with importance sampling or peaks-over-threshold where supported;
4. bootstrap primary sampling units and monitoring strata, refit the full chain, and report an upper uncertainty bound `q_U`;
5. compare body/tail families and dependence scenarios.

The executable scenario intentionally stops short of claiming that its 2–3 million ordinary Monte Carlo draws precisely identify `q_0.99999`. That limitation is an observed result, not hidden by extra decimals.

## Primary evaluation rule

Compute `ρ=q/T` and `ρ_U=q_U/T` only after unit and standard provenance checks. Apply the noncompensatory class in `evaluation-target.md`. Optional triage is lexicographic by class, `ρ_U`, `ρ`, and affected population. Coverage/sample size are displayed as evidence quality and do not offset an exposure violation.

## Improvement over baseline

The improvement targets observed defects rather than substituting algorithm names:

- censored likelihood replaces nondetect=zero;
- crosswalk conservation replaces ad hoc taxonomy merging;
- design/transport weights replace unqualified pooling;
- uncertainty upper bounds replace a single extreme-tail point estimate;
- a hard gate replaces fully compensatory safety scoring;
- score/quantile/probability semantics are separated before ranking.

In the synthetic experiment, the censored parametric point estimate reduces relative tail error from about `-59.7%` to `-15.2%`. That is a measurable improvement but not closure: replicate tail estimates and ±10% contamination-scale scenarios remain wide. The point estimate therefore cannot by itself support a safety declaration.

## Method selection and failure modes

| Candidate | Why suitable | Assumptions | Compensation | Data needs | Main failure mode | Interpretation |
|---|---|---|---|---|---|---|
| Nondetect-zero empirical baseline | minimal and directly tests source warning | representative empirical samples, independence | none in exposure; equal-weight secondary score is compensatory | intake and monitoring samples | severe downward bias, unstable tail | baseline only |
| Censored hierarchical exposure model + hard gate | matches censoring, sparse strata, unpaired data, and source quantile | family/tail/dependence/transport assumptions declared | no compensation at compliance gate | designs, LODs, units, standards, taxonomies | model-form and extreme-tail uncertainty | primary conditional model |
| Distribution-free worst-case bounds | useful fallback when tail family unverifiable | bounded supports/moments | noncompensatory | defensible physical/regulatory bounds | bounds may be too wide to decide | conservative fallback |

AHP, entropy weights, TOPSIS, PCA, and fuzzy evaluation are not selected because the source's primary target is not a preference-weighted alternative score.
