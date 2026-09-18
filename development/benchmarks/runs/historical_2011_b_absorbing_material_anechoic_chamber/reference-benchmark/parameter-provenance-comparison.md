# Parameter provenance comparison

## Problem-given quantities

The common given quantities are chamber dimensions, source trajectory and duration, quiet-zone geometry, the requirement `gamma <= 0.03`, and the two material cases `rho=0.50` and `rho=0.05`.

## Derived or numerical quantities

Reflection count, incidence angles, image coordinates, wall coupling coefficients, quadrature weights and solver tolerances are derived or numerical controls. They should not be presented as measurements.

## Added assumptions visible in the references

- canonical tip/vertex entry (B10286058 and special B10319002 cases);
- uniform incidence-angle distribution (B10293022);
- finite dominant reflection region (B10145011);
- 600-reflection cutoff (B10386003);
- random reflection direction in a Monte Carlo approximation (B90045020);
- one-bounce-only Q2 mechanism (B90005018).

These assumptions are not automatically wrong. The issue is whether they are labelled and whether the result is sensitive to them. Several papers state them in prose, but the result tables often do not separate assumption sensitivity from solver precision.

## Comparison with the Blind Run

The Blind Run marks `rho`, room data and motion data as `GIVEN`, image order and quadrature as numerical controls, and source normalization as an assumption that cancels from gamma. It also marks Q1 entry coordinate and wedge scale as added closure assumptions. This provenance discipline is stronger than the average reference presentation.

The remaining limitation is material: an effective scalar rho is not a full complex, frequency-dependent reflection coefficient. No reference supplies enough independent data to identify the full response.
