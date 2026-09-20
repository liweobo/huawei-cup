# Assumptions And Unresolved Inputs

All rows below are MODELING_ASSUMPTION, never PROBLEM_GIVEN_FACT.

| ID | Assumption or unresolved issue | Use and claim restriction |
|---|---|---|
| A01 | OD tonnes refer to a representative operating day | Required for daily optimization; attachment time basis is missing, so NOT activated for official data. |
| A02 | A year has 365 depreciation days | Daily capital charge = capital * 0.01 / 365. If operation days differ, replace denominator. |
| A03 | Coordinates are planar, with metres convertible to kilometres | Only usable after the missing coordinate reference is audited. Straight length is a lower-bound planning surrogate, not surveyed tunnel length. |
| A04 | Normal state seeks congestion index <=4 in each region | Interprets 'at least basically unobstructed'; exactly 4 is a class boundary and needs policy clarification. Park underground share is maximized first among congestion-feasible solutions. |
| A05 | At most 90 aggregate departures per node per day | Conservative interpretation of 'each node' 5/hour for 18 hours; interchange counting and per-direction versus all-direction interpretation require validation. |
| A06 | Feasible corridor eligibility must precede construction | No real corridor set is available. No all-pairs or threshold-generated real candidate graph is built. Engineering obstacles are expressly set aside by the problem, but actual constructability is not certified. |
| A07 | Demand can be divided into commodities | Parametric continuous flow model. Train counts and carriage counts are integer. A route-only static check is not an operational timetable. |
| A08 | Generic single-physical-tunnel removal with both directions disabled | Tests the prompt's channel interruption. No failure probability is asserted. |
| A09 | Annual demand D(t)=D(0)*1.05^t, t=0 base year | Growth rate is given; base-year convention is explicit. No forecast fit is claimed. |
| A10 | Eight annual length budgets require a tolerance epsilon | 'Roughly equal' has no numerical tolerance. Keep epsilon symbolic; no arbitrary schedule. |

The oracle is SCENARIO_ASSUMED / SYNTHETIC_CODE_VALIDATION. Its eight nodes, coordinates, eight eligible corridors, six directed OD pairs, memberships, symmetric engineering lengths and carriage choices are artificial test inputs. They are not replacement attachments. They prove implementation behavior only.

No stochastic simulation, failure probability, monetary multiobjective weight, pixel-to-metre calibration, hidden spatial aggregation or road-distance proxy is introduced.
