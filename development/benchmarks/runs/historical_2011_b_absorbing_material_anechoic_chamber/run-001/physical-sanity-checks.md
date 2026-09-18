# Physical sanity checks

| Check | Expected behavior | Observed behavior | Status |
|---|---|---|---|
| Power reflection coefficient | `0 <= rho cos(a) <= rho <= 1` | Reflected factors nonnegative and bounded; zero reflectivity gives zero output | PASS |
| Unit ray direction | Norm remains one after reflection | Max norm error `3.33e-16` | PASS |
| Boundary/interface closure | Hit point lies on selected plane; incidence/reflection angles match | Plane error `1.78e-15 m`; angle error `1.67e-16` | PASS |
| Translation symmetry along infinite wedge | x component is unchanged | Max x-component error `0` | PASS |
| Energy accounting in Q1 | reflected + removed + escaped = initial | Max balance error `2.22e-16` | PASS |
| 3D vs projected 2D | 3D path weight equals 2D weight times transverse-speed^N | Max identity error `5.55e-17` | PASS |
| Right-angle limiting wedge | Normal incidence in 90-degree V gap gives two hits and weight `rho^2/2` for rho=0.5 | Computed two hits, weight `0.12500000000000003` | PASS |
| Material monotonicity | Higher rho should not lower reflected power in this positive power-sum model | rho=0.05 <= rho=0.50 for every time sample | PASS |
| Motion symmetry | Symmetric room/source motion gives gamma(t)=gamma(4-t) | Max error `2.22e-16` | PASS |
| No-reflection limit | rho=0 gives gamma=0 | Computed exactly 0 | PASS |
| Receiver/source scale | Multiplying source intensity should cancel from gamma | Scale-cancellation error 0 | PASS |
| Edge policy | Exact apex/corner events have undefined facet normal under no-diffraction model | Explicitly returned `EDGE_UNDEFINED`; not silently assigned | PASS |

These are checks of conservation-like and geometric properties of the chosen model. They are not independent physical experiments.
