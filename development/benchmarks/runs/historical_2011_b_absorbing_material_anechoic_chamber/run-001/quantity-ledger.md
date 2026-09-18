# Quantity / unit audit

Source labels Fxx refer to `problem-facts.md`. PROBLEM_GIVEN_FACT and EXTERNAL_DOMAIN_KNOWLEDGE are never interchangeable. Rad and sr are SI dimensionless derived units, retained as semantic labels.

| Symbol | Meaning | Unit | Source / provenance | Known or unknown / range | Role |
|---|---|---|---|---|---|
| B,H,L,b,R,s | chamber width,height,length,arc offset,radius,patch side | m | p4 GIVEN | 18,14,15,1,14,0.3 | fixed geometry |
| h,d | wedge height and pitch | m | Fig2 GIVEN symbols | unknown positive; not measured | parametric geometry |
| α | wedge half-angle | rad | Fig2 GIVEN symbol | 0<α<π/2; d=2h tanα DERIVED | geometry |
| θ,φ | incoming polar and azimuth angles | rad | Fig3 GIVEN symbols | 0≤θ<π/2; signed φ convention explicit | ray input |
| y₀/d | wedge entry fraction | dimensionless | DERIVED required input | (0,1), excluding exact edge hits | closes individual path |
| a_j | angle of incidence at bounce j | rad | F02 GIVEN meaning, DERIVED from u,n | 0≤a≤π/2 | reflectivity |
| ρ₀ | normal power reflection coefficient | dimensionless | GIVEN 0.50 or 0.05 for Q2 | [0,1] in validation cases | material surrogate |
| r_j=ρ₀ cos a_j | local power reflection coefficient | dimensionless | F02 DERIVED | [0,ρ₀] | attenuation |
| I,I_N,I_* | radiant intensity, axial intensity, initial scale | W/sr | F03,F10 GIVEN; I_* unknown | I_N(t)=I_*(1+t/4s) DERIVED | source |
| w | surviving ray power/intensity fraction | dimensionless | DERIVED | [0,1] | Q1 intensity relative to 1 |
| Φ,P | flux / power | W | F10–F16 GIVEN definition | nonnegative | integrated receiver power |
| E,M | irradiance / exitance | W/m² | F13,F16 GIVEN | nonnegative | density |
| γ | reflected/direct received power | dimensionless | F05 GIVEN | nonnegative; required ≤0.03 | primary metric |
| t,T | motion time,duration | s | p4 GIVEN | t∈[0,4],T=4 | known simulation coordinate, no forecasting |
| ψ,β | apparent-source azimuth,total arc angle | rad | β=45° GIVEN, ψ=−β/2+βt/T DERIVED | ψ∈[−π/8,π/8] | source position |
| p,S,Q,q | point/source/center/patch point coordinates | m | DERIVED from Fig6 | room bounds | geometry |
| u,n,a | ray unit direction,facet normal,source axis | dimensionless | DERIVED / reflection law EXTERNAL | Euclidean norm 1 | direction geometry |
| ℓ,D | segment length,total unfolded path length | m | DERIVED | positive | intersections and inverse-square spreading |
| A,dA | receiving area | m² | GIVEN/DERIVED | A=s²=0.09 | area quadrature |
| ω | solid angle | sr (dimensionless) | F06–F09 GIVEN | 0…4π | radiometry |
| N,kx,kz,m,n_y | bounce count and image indices | dimensionless integers | DERIVED | finite truncation then convergence | numerical summation |
| f,λ | frequency,wavelength background | Hz,m | p2 GIVEN | 0.3–300 GHz; 1m–1mm | not needed in prescribed power/ray model |
| n_q,Δt,K | quadrature order,time spacing,bounce cutoff | integer,s,integer | ASSUMED numerical settings | convergence study, not material constants | numerical controls |

## Dimensional consistency for every main equation

1. F02 multiplies two dimensionless numbers. Reflectivity is a power ratio: repeated path weighting multiplies r_j directly; it does **not square** r_j.
2. Plane intersection ℓ=−F(p)/(n·u): F(p) has m, denominator dimensionless, ℓ has m. Reflected u'=u−2(u·n)n is dimensionless. Travel update p'=p+ℓu adds m to m.
3. w_out=∏r_j and w_abs=Σw_before(1−r_j) are dimensionless. I_out=I_in w_out has W/sr when absolute I is known.
4. S=(R sinψ,L−R cosψ,0) has m throughout. I_N=I_*(1+t/T) uses a dimensionless time ratio; β is converted to rad before trigonometry.
5. dP=I_N max(a·u,0) |u_y| dA/D² ×∏r_j: dA/D² represents sr; W/sr × sr gives W. The numerical use of sr=1 is explicit, not addition of incompatible units.
6. γ=ΣP_ref/P_direct is dimensionless. Both share the same I_N and receiving area; intensity normalization cancels exactly.
7. Sensitivity compares γ or watts normalized by I_*, not differences between units. No empirical fitting, complex material parameters, amplitude ratios, or dB are used. If dB were reported, power convention would be 10 log10 γ; no such conversion enters decisions.

**Dimensional result: PASS for the defined model.** Input uncertainty/model validity is a separate issue from dimensional closure.
