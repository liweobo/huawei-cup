# Problem facts

Facts below come from the corrected DOC/PDF pair. Assumptions are labelled separately.

## Q1 — meteorology/visibility relation

- `PROBLEM_GIVEN_FACT` target: airport visibility, operationalized by supplied `MOR_1A` in metres.
- `PROBLEM_GIVEN_FACT` input: surface meteorology such as temperature, humidity, wind, and the AMOS attachment.
- `PROBLEM_GIVEN_FACT` time scope: contemporaneous observations in two supplied fog episodes; no future horizon is stated.
- `PROBLEM_GIVEN_FACT` required output: a concrete relationship/model between visibility and meteorological factors.
- `MODELING_ASSUMPTION` evaluation: hold out each entire event in turn; report out-of-event error. This is same-time estimation/association, not future forecasting and not causation.

## Q2 — airport-video visibility estimation

- `PROBLEM_GIVEN_FACT` target: same-time visibility from airport video, supervised by AMOS visibility.
- `PROBLEM_GIVEN_FACT` input: airport video plus AMOS observations.
- `PROBLEM_GIVEN_FACT` required output: a deep-learning video estimator and an accuracy assessment.
- `PROBLEM_GIVEN_FACT` attachment dependency: airport video is essential.
- `SOURCE_ATTACHMENT_UNAVAILABLE`: no valid paired image/AMOS dataset can be formed; clock tolerance and frame-label alignment therefore cannot be audited. The subproblem is not fabricated.

## Q3 — highway video estimation

- `PROBLEM_GIVEN_FACT` target: visibility estimated from highway video alone.
- `PROBLEM_GIVEN_FACT` input: 100 supplied BMP frames.
- `PROBLEM_GIVEN_FACT` location: a single supplied highway scene.
- `PROBLEM_GIVEN_FACT` required output: algorithm, implementation discussion, and a time curve.
- `PROBLEM_GIVEN_FACT` labels: no instrument visibility series is supplied.
- `MODELING_ASSUMPTION` retained output: fixed-ROI dimensionless contrast proxy. It is a relative scene indicator, not verified MOR metres.

## Q4 — trend and dispersal-time forecast

- `PROBLEM_GIVEN_FACT` input: Q3 time curve.
- `PROBLEM_GIVEN_FACT` required outputs: future strengthening/weakening trend and dispersal time for a specified visibility, exemplified by MOR = 150 m.
- `PROBLEM_GIVEN_FACT` horizon: no single fixed horizon is stated.
- `MODELING_ASSUMPTION` diagnostic horizons: 1, 3, and 6 sampled frames (approximately 0.69, 2.08, and 4.17 minutes) for the available relative proxy.
- Absolute 150 m crossing time is `NOT_IDENTIFIABLE_FROM_AVAILABLE_ATTACHMENTS` because no calibrated mapping from the proxy to MOR exists.

## Definitions and units

- MOR and RVR are distinct operational visibility quantities; retained target field is explicitly named.
- AMOS visibility is in metres; temperature °C, relative humidity %, pressure hPa, wind speed m/s, direction degrees before sine/cosine encoding.
- Highway proxy is dimensionless.
- The problem’s atmospheric attenuation and contrast formulas provide physical context but do not supply image-scene calibration.

## Estimation/forecast boundary

Q1–Q3 concern current/same-time estimation. Only Q4 calls for future forecasting. The Q1 event-holdout score is not reported as Q4 forecast evidence.
