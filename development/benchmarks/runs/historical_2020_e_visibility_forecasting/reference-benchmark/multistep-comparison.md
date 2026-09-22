# Multistep comparison

| ID | Strategy | Horizon definition | Common-origin comparison | Assessment |
|---|---|---|---|---|
| Frozen | DIRECT separate 1/3/6-frame and 5/15/30min models | explicit target frame/time | explicit common origins | PASS |
| R1 | CURVE_EXTRAPOLATION, Holt | 160 future steps; 40s grid | none | no per-horizon validation |
| R2 | CURVE_EXTRAPOLATION, linear + GM | clock regression / 0.69min steps | none | origin/count ambiguous |
| R3 | CURVE_EXTRAPOLATION, cubic | extended x index at 42s | none | no per-horizon validation |
| R4 | recursive ARIMA/GM and cubic extrapolation | 42s intervals informally | none | models point in different directions |
| R5 | ARIMA extrapolation + RECURSIVE Seq2seq | decoder 2 steps, then recursion; 41.25s stated | none for final crossing | short-step RMSE cannot support long crossing |
| R6 | PSO-NGBM curve + recursive ARMA | samples at claimed 42s | none | fit MAPE only |

Existing Skill material specifies targets, horizons, rolling evaluation and future-field restrictions, and the frozen run executed separate direct horizons correctly. Named DIRECT/RECURSIVE/DIRREC/MULTI_OUTPUT taxonomy is terse in the Skill, but that brevity did not cause a frozen-run correctness failure and therefore fails G1 criterion 2.
