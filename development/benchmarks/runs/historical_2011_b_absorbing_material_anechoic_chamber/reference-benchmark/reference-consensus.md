# Reference consensus

## Stable findings

1. The flat absorber case `rho=0.50` does not meet `gamma <= 0.03` in the references that compute a full or dominant reflected power model.
2. The better absorber case `rho=0.05` generally meets the threshold under the authors' chosen approximations.
3. The minimum is normally near `t=2 s`, when the source is at the arc midpoint.
4. Cosine incidence factors, repeated reflection attenuation and finite chamber geometry matter.
5. Q1 reflection count and attenuation depend on entry geometry; a canonical tip/vertex case is an extra assumption.

## Non-consensus findings

The rho=0.05 gamma value is not stable across model families. The reference range is roughly 0.0035 to 0.0218, with B10386003 lower by several orders of magnitude under its virtual-image truncation. The frozen Blind Run is about 0.0297, at the high end and close to the requirement.

The disagreement is not explained by roundoff. It reflects different choices about finite-area integration, wall coupling, image-path populations, one-bounce truncation, material-angle law and random versus specular reflection.

## What consensus does not establish

The papers do not establish a measured chamber performance guarantee, a unique physical solution, a validated full-wave model, or an award ranking. They are reference implementations and arguments, not independent ground truth.
