# Data audit

## AMOS

- Two entities/events: AMOS20191216 and AMOS20200313. They are not concatenated as if adjacent in time.
- Per event: PTU has 1,440 one-minute rows; VIS and WIND each have 5,755 roughly 15-second rows.
- Local spans are 2019-12-15 08:00–2019-12-16 07:59:45 and 2020-03-12 08:00–2020-03-13 07:59:45.
- Resampling grid: timestamps are floored to Beijing-local minute; numeric readings within a minute use the median; the three sensor families are inner-joined on minute.
- Result: 1,440 rows per event, no missing cells, no duplicate event-minute pairs, no non-one-minute steps.
- `MOR_1A` range is 0–10,000 m. There are 518 values at or below 50 m and 225 at 10,000 m. These tails are treated as censored/special instrument behavior, not ordinary high-precision continuous observations.
- AMOS20200313 differs materially from AMOS20191216: median 3,200 vs 5,000 m, 421 vs 223 observations at or below 150 m, and 225 vs 0 observations at 10,000 m. Two-sample KS statistic is 0.375 (descriptive p≈1.59e-90); the held-out event is a regime-transfer test.
- Timezone is supplied explicitly by the field name. No UTC/local conversion is needed because all merges use `LOCALDATE (BEIJING)` consistently.

## Highway screenshots

- 100 ordered BMP frames, all 1280×720, no missing frame number.
- Visible timestamps on frames 1/25/50/75/100 support an approximately regular 41.67-second sampled sequence from 06:30:26 through 07:39:11.
- A fixed ROI `(120,220)–(850,650)` excludes the timestamp and location overlays. No frame-specific cropping was selected after observing forecast performance.
- Derived series: the 90th percentile Sobel magnitude divided by mean luminance. It is dimensionless and scene-relative.
- There are no paired highway MOR labels, calibrated landmark distances, or multi-scene repetitions. Absolute visibility accuracy and 150 m event metrics cannot be computed.

Machine-readable details are in `outputs/amos_data_audit.json`, `outputs/amos_distribution_shift.json`, and `outputs/highway_proxy_audit.json`.
