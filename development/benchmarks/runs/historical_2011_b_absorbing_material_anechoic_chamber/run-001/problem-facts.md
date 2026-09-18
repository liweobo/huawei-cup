# Problem facts — FROZEN before simulation

All entries here are **PROBLEM_GIVEN_FACT**, from the retained original DOC, SHA256 `c44d22cb08b5f868357b0fdbd7bdaec1db4b7db1208f40e8324c5eb0716ede89`. Page references mean the retained seven-page parser rendering, not an independently asserted original Word pagination. All seven page images were visually inspected; parser text alone drops MathType formulas and is insufficient. Conversion evaluation watermarks are not source content.

## Scope and required outputs

The title is “2011年全国研究生数学建模竞赛B题：吸波材料与微波暗室问题的数学建模”. The problem asks for simple, intuitive **geometric optics** models, followed by analysis and numerical calculation; subsequent experimental measurement/correction is explicitly outside scope (p2). The introductory aircraft and equipment examples and the target-array operating principle are context, not additional optimization tasks.

| ID | Required output | Given inputs/constraints | Source |
|---|---|---|---|
| Q1 | Quantitative final reflected-ray direction, reflection count, and intensity as functions of reflectivity and geometry | Infinite wedge length along x; uniform material; input intensity 1 unit; reflect only at interfaces; ignore edge diffraction; may begin in 2D | p2, Figs 2–3 |
| Q2-flat | Compute reflected/direct received-power ratio γ throughout the 4-second apparent-source motion; decide whether γ≤0.03 always; locate minimum | Six reflecting walls, flat absorber ρ=0.50; cosine source; no wall scattering; neglect antennas/supports/receiver disturbance | pp3–4, Figs 4–6 |
| Q2-effective | Repeat Q2 with effective normal reflectivity ρ=0.05 | This average is already supplied; replace wedges by an equivalent better flat absorber, not an instruction to estimate this value from Q1 | p4 |

## Given geometry, constants and domains

- Wedge included angle is **2α**, height h, base width d (Fig2); numerical h,d,α are not supplied. Fig3 uses x along infinitely long ridges, y transverse, z upward; origin O is a ridge tip. Incidence θ is angle between +z and the negative incident-ray direction; azimuth φ is angle between +x and the ray projection in xOy. No signed azimuth branch or landing coordinate is specified.
- Normal reflectivity is denoted ρ, incidence angle in the general cosine law is also denoted α. This reuses the wedge half-angle symbol: the implementation must rename incidence angle, not conflate them.
- Chamber width B=18 m, height H=14 m, length L=15 m, arc offset b=1 m, arc radius R=14 m (p4). All dimensions start at absorber tip planes.
- Figs4/6: arc lies in central horizontal plane, symmetric about the chamber longitudinal centerline; arc center equals quiet-zone center at the right end wall; arc midpoint is b from the left end wall. Fig6 uses x transverse, y longitudinal, z vertical; quiet patch is in the xz plane at the right wall.
- Total angular extent β=45°, one physical antenna every 3°, 16 antennas. Axes point toward arc center. The modeled **apparent antenna** moves continuously from one end of the arc to the other with constant angular speed in 4 s; axial intensity rises linearly to twice its initial value. No absolute initial intensity is supplied.
- Quiet zone is a square of area s×s, s=0.3 m. The specified metric is **sum of reflected powers / direct source power**, γ≤0.03 at all times; no dB metric is given.
- Frequency background: microwave 0.3–300 GHz (wavelength 1 m–1 mm). No operating frequency, complex permittivity/permeability, phase response, roughness, thickness, or measured calibration data are supplied or requested for the simplified model.
- Q1 does not give a distribution of ray landing locations. Q2 does not give angle-dependent measurement data beyond the imposed cosine law.

## Given equations, transcribed from visible source objects

| Fact ID | Equation | Source / meaning |
|---|---|---|
| F01 | ρ=P_r/P_i; ρ<1 | p1; **power** reflectivity, not field-amplitude coefficient |
| F02 | ρ(a)=ρ cos a | p1; a is angle of incidence from surface normal, renamed here to avoid α collision |
| F03 | I_i=I_N cos i | p3 and p6, f2.2; source axial intensity I_N; f2.2 gives −π/2≤i≤π/2 |
| F04 | ∠AOP/∠BOP=P_B/P_A | p3, Eq(1); given apparent-target background, not independently recalibrated |
| F05 | γ=(sum of wall-reflected powers)/(direct source power)≤0.03 | p4 |
| F06 | dω=dS/R² | p5, f1.1; perpendicular spherical area |
| F07 | dω=(n·dS_vector)/R²=cos a dS/R² | p5, f1.2; oriented/projected area |
| F08 | dS=(R sin i dφ)(R di)=R² sin i di dφ; dω=sin i di dφ | p5, f1.3; i measured from polar axis as drawn |
| F09 | ω=∫₀²π∫₀π sin i di dφ=4π | p5, f1.4 |
| F10 | I=dΦ/dω | p5, f2.1; W/sr |
| F11 | Φ=∫I(i,φ)dω=∫₀²π∫₀π I(i,φ)sin i di dφ | p6; the middle printed expression abbreviates the angular integral |
| F12 | I(i,φ)=I(i) ⇒ Φ=2π∫₀π I(i)sin i di | p6 |
| F13 | E=dΦ/dS; E₀=Φ/S | p6, f2.3; W/m² |
| F14 | E=4πI₀/(4πR²)=I₀/R² | p6, f2.4 |
| F15 | dω=cos θ dS/r²; dΦ=I₀dω=I₀ cos θ dS/r²; E=(I₀/r²)cos θ | pp6–7, f2.5 |
| F16 | M=dΦ/dS; M=ρE | p7, f2.6 and subsequent text; reflected exitance W/m² |

The prose calls i a “高低角”, while the figure and sin(i) Jacobian define a polar angle; the model uses the explicit figure/formula convention. The raw text's “功率…能量” wording does not change Φ's explicitly supplied W unit.

## Figures and attachments

- Fig1: direct, once-reflected and twice-reflected signals in a chamber; illustrates unwanted returns.
- Fig2: wedge cross-section, multiple reflections and transmitted paths, h,d,2α; transmission appears in motivation, while Q1's requested scope is interface reflection within one gap.
- Fig3: infinite ridges and x,y,z directions.
- Fig4: chamber, arc array, receiving location, B,L,b and included array angle.
- Fig5: two neighboring sources and the apparent direction with Eq(1).
- Fig6: full chamber and top view, quiet patch orientation and arc placement.
- Appendix Figs1–4: solid angle, spherical-coordinate element, cosine emitter, inclined receiving area.
- There are no numerical data tables. The directory listing has only A/B/C/D documents and `.DS_Store`; no separate B attachment is listed. The two appendices and all parameters above are inside the DOC.
- Source bibliography lists Liu Shunhua et al. (2007), Gurn/Hiziroglu translated textbook (2000), and Zhang Yimo (1988). These bibliography entries were extracted but the works were **not accessed**.

## Extraction status

**No unresolved EXTRACTION_UNVERIFIED item used by the model.** Complete substantive prose is present through the bibliography in both independent raw-main-stream and parser text. All formula-bearing pages and all ten figures were visually checked. Original retained; converted DOCX/HTML and parser dependencies are temporary, excluded from Git. Verified fact freeze is separately SHA256 recorded before model execution.
