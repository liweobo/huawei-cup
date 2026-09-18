# Frozen current-skill solution

This file freezes the completed Blind Run before reading any 2011B excellent-solution reference. It is a post-hoc comparison baseline and does not modify `run-001`.

## Identity and integrity

- Benchmark: `historical_2011_b_absorbing_material_anechoic_chamber`
- Blind run: `run-001`
- Blind-run report: `../run-001/REPORT.md`
- Starting Git HEAD for this post-hoc phase: `991e8aa93f1383f5ae94f5ba90d6d02c5d9f91b1`
- Starting branch: `main`
- `skill/` tree hash at phase start: `ea0be7810800d452c1703407becc9b45a5e51722`
- Original question SHA256: `c44d22cb08b5f868357b0fdbd7bdaec1db4b7db1208f40e8324c5eb0716ede89`

## Frozen formulation

The Blind Run read the original DOC and retained the problem facts separately from external physics knowledge. It treated Q1 as an infinite triangular wedge with specular power reflection and Q2 as a finite six-wall chamber with a moving apparent source, a finite quiet-zone square, cosine emission, cosine incidence reflectivity, and an explicitly supplied effective reflectivity.

### Q1

- State: ray position, unit direction, surviving power fraction, bounce count, and per-hit attenuation.
- Inputs: wedge height/angle (or height/pitch), normal power reflectivity, incidence polar/azimuth angles, and an added entry coordinate `y0`.
- Outputs: final direction, exit point, reflection count, and surviving intensity fraction.
- Geometry: two planar facets, an escape plane, and an unbounded ridge direction.
- Law: `u' = u - 2(u dot n)n`; local power factor `rho cos(a)`.
- Status: exact event tracing in 2D and an extruded 3D extension. The model returns a parametric result because the statement does not specify the entry point or numerical wedge dimensions.

### Q2

- Geometry: `B=18 m`, `H=14 m`, `L=15 m`, `R=14 m`, `b=1 m`, `s=0.3 m`, `beta=45 deg`, duration `T=4 s`.
- Source: apparent source moves on the prescribed arc; axial intensity rises linearly to twice its initial value.
- Baseline: direct power plus one reflected bounce.
- Mechanism model: direct power plus all six-wall specular image paths up to reflection order `K`, integrated over the finite quiet-zone square.
- Metric: `gamma = reflected power / direct power`; the source normalization cancels from `gamma`.
- Numerical controls: image-order refinement through `K=40`, Gauss-Legendre area orders `1,3,5,9`, time grids of 81 and 161 points, and an all-time upper-bound certificate.

## Frozen results

- Q1: 144 deterministic parameter scenarios; norm, equal-angle, energy accounting, 2D/3D projection identity, limiting-case, and entry-grid checks passed.
- Q2 with `rho=0.50`: `gamma` range approximately `0.39245849-0.39485913`; fails `gamma <= 0.03`.
- Q2 with `rho=0.05`: `gamma` range approximately `0.02966885-0.02973729`; all-time upper certificate `0.02986864055 < 0.03` within the stated model.
- A simulated +10% reflectivity perturbation around `rho=0.05` gives approximately `gamma=0.03280`, showing a narrow material-margin sensitivity.
- Numerical convergence and image-path/explicit-trace agreement passed at the reported precision.

## Frozen evidence discipline

- Problem facts, assumptions, external sources, quantities, model equations, numerical outputs, and validation evidence are separated in `run-001`.
- No calibration data or independent chamber measurement exists.
- No complex material response, phase, diffraction, scattering, or frequency dependence was inferred.
- `rho=0.50` and `rho=0.05` are problem-given Q2 cases; no fitting was performed.
- The original Blind Run conclusion was `GENERALIZABLE_MECHANISM_GAP_FOUND`, with the candidate `MECHANISM_MODEL_CLOSURE_GATE`, classified P1.

## Explicit post-hoc boundary

The files under `../run-001/` are read-only comparison inputs. Excellent papers are post-hoc references only. This file must not be revised to match any reference method or result.
