# Mathematical model and closure

## Model hierarchy and dependency

Facts → geometry/unit audit → Q1 2D wedge baseline → Q1 3D extruded wedge;
Facts → Q2 direct + one-reflection baseline → repeated specular reflection by unfolding → finite-area integration → convergence/physical validation.
Q2's given effective ρ=0.05 is **not** calibrated to the illustrative Q1 results. No model zoo, material inverse problem, Maxwell solver or stochastic optimizer is needed.

## Q1: triangular air gap

**State:** location p=(x,y,z), unit propagation u, surviving power fraction w, bounce count N, per-hit ledger. **Inputs:** h,α (or h,d with d=2h tanα), normal power coefficient ρ₀, entry y₀∈(0,d), incidence θ, signed azimuth φ. **Output:** exit direction, exit point, N, w, or EDGE_UNDEFINED. **Initial condition:** p=(0,y₀,0), w=1, N=0, u=(sinθ cosφ,sinθ sinφ,−cosθ). This defines φ from the propagation projection; the source's unsigned figure is not treated as a different signed convention.

Air lies between the facets

F_L=cosα·y+sinα·z≥0,
F_R=cosα·(d−y)+sinα·z≥0,
−h≤z≤0, x unrestricted.

Inward normals are n_L=(0,cosα,sinα), n_R=(0,−cosα,sinα). For each n·u<0, candidate hit distance ℓ=−F(p)/(n·u)>0. Select the nearest valid facet or, if u_z>0, the escape at z=0. Ties at an apex/tip are excluded edge events, not assigned an invented normal.

**Interface law:** u'=u−2(u·n)n, c=−u·n∈[0,1], r=ρ₀c, w'=wr. Removed weight w(1−r) is recorded. No transmitted channel or unknown refractive index is fabricated. Geometry is closed by the two facets and escape plane; ridge direction is unbounded. The process is event based, not a time-step field simulation.

**2D baseline:** x-velocity zero, same yz triangle and exact event intersections. **3D improvement:** retain u_x and use the full normal dot product. For s_perp=√(u_y²+u_z²)>0, the projected 2D direction is (0,u_y/s_perp,u_z/s_perp). Both have identical yz paths and N; 3D keeps u_x unchanged and has w_3D=s_perp^N w_2D. This is an independent analytic cross-check. Ignoring x would incorrectly overstate reflection under the *given* cosine-reflectivity law.

**Validation:** unit direction norm, tangential component, equal incidence/reflection angles, each hit on its plane, no escape through solid, nonnegative attenuation, removed+escaped=1, scale invariance, 90° V-groove with perpendicular incoming ray yields two bounces and w=ρ₀²/2 away from the central edge; 3D/2D identity. Sample-average convergence concerns the optional uniform-landing illustration, not individual event accuracy.

## Q2: chamber geometry and source

**State/quantities:** per-path irradiance and integrated incident power, not an evolving electromagnetic field. **Parameters/inputs:** the GIVEN B,H,L,R,s,β,T,ρ₀ and time t. **Outputs:** P_direct/I_*, P_reflected/I_*, γ(t), minimum time, all-time threshold assessment. **Geometry:** x∈[−B/2,B/2], y∈[0,L], z∈[−H/2,H/2], Q=(0,L,0), patch q=(x,L,z), |x|,|z|≤s/2. Origin is center of the left end wall; x transverse, y toward quiet zone, z up. All six reflecting boundaries are the absorber tip planes. Their inward normals are ±Cartesian basis vectors.

ψ(t)=−β/2+βt/T,
S(t)=(R sinψ,L−R cosψ,0),
a(t)=(Q−S)/R,
I_N(t)=I_*(1+t/T),
I(u,t)=I_N max(a·u,0).

Arc midpoint y=L−R=b=1 m, so redundant source geometry checks exactly. The normalized I_*=1 W/sr is not a measured power. No initial field condition is required for the quasi-static power model.

## Q2: one-bounce baseline and repeated-reflection mechanism

Specular rays are unfolded into straight lines by reflecting the receiver. For kx,kz∈Z and n_y∈{0,1,…}, receiver images are

q_im=(kx B+(−1)^kx x, Y(n_y), kz H+(−1)^kz z),

Y(n_y)=(n_y+1)L for even n_y, and Y(n_y)=−n_y L for odd n_y.

The reflection counts are N_x=|kx|, N_z=|kz|, N_y=n_y, N=N_x+N_y+N_z. This parametrization removes duplicated receiver images at the boundary y=L. The final reception is measured **before** a terminal reflection; it is not multiplied by another ρ. Earlier visits to other end-wall positions do reflect. The patch is a nonperturbing monitor, consistent with neglecting receiver influence.

Let v=q_im−S, D=||v||, u=v/D. Reflection preserves absolute Cartesian direction components, hence path weight

W=(ρ₀|u_x|)^N_x (ρ₀|u_y|)^N_y (ρ₀|u_z|)^N_z,

where any exponent zero gives factor 1, including 0^0 in this combinatorial product. Reflected power from patch element dA is

dP=I_N max(a·u,0) |u_y| W dA/D².

The source cosine and receiving cosine have different roles and neither is a reflection coefficient. **There is no additional inverse-square factor for every bounce**: an unfolded specular path spreads over its total path length D. Treating each patch of wall as a Lambertian source would introduce unprovided scattering.

The N=0 image gives direct power. Sum N=1 for the baseline; sum 1≤N≤K for the mechanism model. Integrate x,z over the same finite square for both. γ=P_ref/P_direct. The common I_N(t) cancels, so source doubling cannot change the γ minimum. It does change absolute normalized received powers.

**Boundary closure:** mirror direction law on all six planes, ρ₀|u·n| power attenuation at each hit, no scattering/refraction, no transmission back into the room, no terminal receiver attenuation. Fold/unfold paths are independently reconstructed for low orders to validate image counts, hit positions and normals. Degenerate corner intersections are measure-zero boundaries and do not create extra paths.

## Numerical protocol and error separation

- Deterministic image enumeration by **total bounce order**, not a cube cutoff mislabeled as bounce order.
- Tensor Gauss-Legendre quadrature on the 0.3m square, orders 1,3,5,9; order 1 is the central-point approximation.
- Main time grid 81 points (0.05s), refinement 161 (0.025s); extrema additionally located with bounded one-dimensional minimization and endpoint comparison. A stronger derivative/interval check is used if threshold margins become comparable to time-sampling uncertainty.
- Compare K=1,2,4,8,16,24,32,40 for ρ₀=0.5; ρ₀=0.05 rapidly converges but shares the same main formulation. No stochastic noise or selected seed.

For rigorous truncation control, there are a_n=2n²+2n+1 distinct images of total order n. δ=s/√2 bounds patch displacement. D≥R−δ; direct power ≥I_N A (R−δ)R cos(β/2)/(R+δ)^4. Since W≤ρ₀^n and both cosines≤1,

γ_tail ≤ C Σ(n>K)(2n²+2n+1)ρ₀^n,
C=(R+δ)^4/[(R−δ)^3 R cos(β/2)].

For 0≤ρ₀<1 the polynomial-geometric tail is evaluated analytically (not truncated again). This deliberately loose positive upper bound separates finite summation error from physics assumptions. It is not meaningful at ρ₀=1; no converged lossless chamber sum is claimed there.

**NUMERICAL ERROR:** finite K, finite patch quadrature, time/optimizer resolution, floating-point intersections. **MODEL ERROR:** imposed cosine reflection, geometrical optics, neglected phase/diffraction/transmitted return/scattering, effective ρ uncertainty, actual antenna pattern. A tiny numerical tail is not a measured accuracy bound for a real chamber.

## Calibration, identifiability and evidence strength

No parameters are fitted. All ρ values are either GIVEN Q2 values or labeled sensitivity/illustrative scenarios. Q1 h=1 is arbitrary scale normalization; results are functions of d/h and entry fraction. Complex parameters and reflection phase are not identifiable and not needed for the prescribed **power sum**. There is no independent experimental validation; equal-angle checks, analytic limiting cases, reciprocal path tracing, symmetry, quadrature/order refinement and sensitivity are weaker internal evidence. Results support only this problem's simplified geometric model, not engineering certification.
