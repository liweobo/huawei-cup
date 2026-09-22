# Interval validation

An 80% sequential absolute-error interval is evaluated after ten earlier errors exist for the same method/horizon. It uses no future residuals and is a prediction interval, not a coefficient confidence interval.

## Airport MOR

| Horizon | Method | n intervals | Coverage | Average width (m) |
|---:|---|---:|---:|---:|
| 5 min | persistence | 33 | 0.939 | 1295 |
| 5 min | direct Ridge | 33 | 0.939 | 3958 |
| 15 min | persistence | 33 | 0.970 | 2498 |
| 15 min | direct Ridge | 33 | 0.970 | 4724 |
| 30 min | persistence | 33 | 0.939 | 2441 |
| 30 min | direct Ridge | 33 | 0.970 | 4664 |

Intervals over-cover their nominal 0.80 level and are wide, especially for Ridge. This reflects small sequential calibration samples, abrupt visibility transitions, caps/floors, and regime shift. Coverage is reported rather than using the band decoratively.

## Highway relative proxy

Coverage for persistence is 0.90/0.95/0.95 and for Ridge 1.00/1.00/0.95 at 1/3/6 frames, with only 20 evaluated intervals per cell. Average widths range from `2.03e-4` to `5.63e-4` proxy units. These bands quantify future proxy uncertainty only; they cannot be converted to MOR metres.

Status: `PASS` for origin-safe construction and empirical coverage reporting; `PARTIAL` for operational calibration because samples are small and highway MOR is unlabelled.
