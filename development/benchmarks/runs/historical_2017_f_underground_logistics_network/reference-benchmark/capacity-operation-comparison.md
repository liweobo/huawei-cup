# Capacity And Daily Clearing

## Source Protocol

Vehicle payload is10t on park-primary tunnels and5t otherwise; trains have
4-8 vehicles. At8 vehicles, payloads are80t/40t per train. The2min line
headway and12min/5-per-hour node dispatch limits coexist.18h operation gives
90 departures at a node under run-002's aggregate interpretation. A per-line
or per-track interpretation is an additional assumption; four tracks do not
automatically double a shared station resource.540 departures from line
headway alone are not a station feasibility certificate.

| Reference | Classification | Capacity evidence | Missing operational evidence |
|---|---|---|---|
| F10256001 p20,pp23-24 |STATIC_ONLY |Daily balance and ground constraints written; displayed ground loads violate bounds |No timed queue, transfer, train precedence or end-state proof |
| F10294003 pp25-29 |STATIC_ONLY |90 departures; larger directional flow selects tracks;5t formula typo and8/hour inconsistency |No aggregate station/line co-schedule or final-arrival audit |
| F10486024 pp17-24 |STATIC_ONLY |Ring directionwise max-flow constraint; table10t/flow contradicts5t formulation |No clearing schedule; overload after failure recognized but not resolved by audited flow |
| F10703002 pp19-29,35-36 |PARTIAL_OPERATION_MODEL |Travel/wait formulas and piecewise time/vehicle appendix fragments |Unmapped to full network, no legal-action/queue/precedence/terminal certificate |
| F10710008 pp12-19 |STATIC_ONLY |Nominal daily capacities and utilization/availability ratios |No dispatch, transfer queues or terminal inventory report |
| F90005027 pp14-15,29 |STATIC_ONLY |Daily balance;5/hour and2min rates related algebraically |No joint schedule, shared-resource occupancy or last-delivery proof |
| FK0263 pp22-29 |PARTIAL_OPERATION_MODEL |Acceleration and single-trip last-arrival calculation gives90,89,90,90 calls; directed core flows |No transfer handling, shared station dispatch, full route precedence or timed inventory proof |
| Frozen run-002 |PARTIAL_OPERATION_MODEL |Real-network state-coupled queue scenarios, payload/headway checks and independent replay |Both tested greedy policies leave freight; acceleration/fleet/empty return/final handling omitted |

Counts:5 STATIC_ONLY,2 PARTIAL_OPERATION_MODEL,0 TIMED_OPERATION_MODEL with
a **full-network clearance certificate** among seven papers. Partial here
credits timed reasoning without overstating it. All seven discuss capacity;
none is credited with fully proving the original daily-clearing requirement.

## What The Frozen Failure Means

At18h run-002 leaves27.478101t with0min handling and143.521733t with12min.
The two legal greedy policies fail. This does not prove that every timetable
on the network fails, or that a better search cannot clear it. Conversely,
static capacities PASS cannot establish that any legal timetable succeeds.

Reference FK0263 makes a useful single-link correction:
`floor((1080 - travel_minutes)/12)+1`, assuming a time-zero departure and
arrival by1080min. Its park2 travel14.35576356min yields89 calls. This neither
handles multi-leg freight nor proves shared node resources. It also adds
acceleration that frozen run-002 explicitly omits. These are protocol/scope
improvements to consider in a future separately authorized solve, not inputs
silently applied to run-002 here.

## Operational Gap Test

The existing `skill/references/stateful-scheduling.md` already includes vehicles,
queues, travel, release and precedence (lines9-16), terminal condition (line31),
resource/queue/time transition invariants (line62), rejection of unfinished
terminal states (line91), and independent final audit (line95).
`skill/references/models/optimization.md` lines11,21,27 activates these rules
when dynamic feasibility matters. Static route sequence alone does not trigger
statefulness; real dispatch and transfer resource evolution do.

Run-002 actually applied this distinction and refused a false daily-clearing
claim. The references do not demonstrate an absent generic operational rule
that caused its unsuccessful greedy policies. Thus unresolved clearance is
an important **solution limitation**, while truthful qualification is a
**SKILL_STRENGTH**. No new scheduling or network module is justified here.
