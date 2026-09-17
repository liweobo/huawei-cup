# Feasibility Discipline Comparison

## Current Skill Evidence

Run-002 and run-003 have the strongest explicit discipline in this
benchmark:

- hard constraints are kept as gates, not soft penalties;
- stateful search uses legal actions and a real transition;
- final result workbooks are independently reopened and audited;
- capacity, position occupancy, region-code legality, final receipt and
  completion are checked;
- heuristic outputs are labelled `BEST FOUND`, never `GLOBAL OPTIMUM`.

Run-003 records zero hard violations on `result31.xlsx` and `result32.xlsx`.

## Reference Evidence

The PDFs generally describe feasibility rules and simulation/position
matrices, but the available papers do not consistently provide:

- an independent replay of the submitted workbook;
- explicit machine-conflict and buffer-capacity audit output;
- a proof that every reported output matrix is executable;
- a solver status/bound with a defensible optimality claim.

This is not a claim that the papers are invalid. It means the supplied
paper text does not establish the same level of independent audit as the
current Skill.

## Classification

| feasibility aspect | current Skill | reference consensus | status |
|---|---|---|---|
| hard rules as hard constraints | explicit run-003 contract | mostly described rules/constraints | SKILL ADVANTAGE |
| machine conflict | simulator/audit | usually described, not always independently checked | SKILL ADVANTAGE |
| buffer capacity | simulator/audit | usually described | SKILL ADVANTAGE |
| return/FIFO direction | explicit state transition | often simulated or modeled | comparable |
| output workbook consistency | independent workbook audit | reporting varies | SKILL ADVANTAGE |
| global optimum claim | rejected without proof | several papers call heuristic solutions optimal/optimal-like | SKILL ADVANTAGE |

## Interpretation

The reference benchmark does not support weakening the current
feasibility contract. Any future optimization improvement must preserve
the current independent audit and incumbent validity rules.
