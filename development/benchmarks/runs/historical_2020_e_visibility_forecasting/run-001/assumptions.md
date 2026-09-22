# Assumptions and claim boundaries

1. The corrected DOC/PDF pair is the formal statement; the shorter DOC is an earlier version.
2. `MOR_1A` is the explicit airport target. RVR is not silently substituted for MOR.
3. Within-minute medians summarize 15-second VIS/WIND readings. This is a modeling aggregation, not a new observation.
4. The two AMOS folders are separate fog episodes. The later event is held out for future-origin evaluation; they are never bridged with lags.
5. Airport Q1 uses contemporaneous meteorology only and supports association/estimation language, not causal or future claims.
6. Highway screenshots are treated as regularly sampled according to visible timestamp anchors. Derived timestamps between anchors are approximate.
7. The fixed ROI contrast statistic is a relative scene proxy. No equation maps it to MOR metres, so absolute Q3/Q4 claims are withheld.
8. The problem’s 150 m example supplies threshold provenance, but it does not supply the missing image-to-MOR calibration.
9. Ridge regularization, lag windows, and horizons are fixed before viewing held-out scores; no hidden candidate search is performed.
10. Sequential intervals use only errors from earlier evaluated origins at the same horizon/method. They are empirical predictive bands, not parameter confidence intervals.
11. No external factual data or standard is used. General statistical methods require no external numerical input.
12. The inaccessible airport video is not reconstructed from reference works.

Status: these assumptions allow methodological and relative outputs but not a complete operational 2020E answer.
