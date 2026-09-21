# 2007A Problem Facts

## Extraction status

`VERIFIED`. The retained 25,600-byte legacy DOC was read by Microsoft Word 16.0 in read-only mode, independently decoded from its OLE piece table, and visually checked on all three rendered pages. It contains no source table, image, equation object, or attached dataset. Mathematical requirements appear as inline text.

## Source-defined tasks

| ID | Requirement | Status in this run |
|---|---|---|
| Q1 | Design an overall food-hygiene safety assurance system and a creative technical route, including data structure, surveys, and information integration. | Modelled conditionally |
| Q2 | Build one or more population food-intake models from very-low-rate household dietary surveys, with manageable workload and pollutant-relevant food categories. The statement explicitly makes this part optional. | Modelled conditionally despite being optional |
| Q3 | Build a contaminant-distribution model from sparse routine/spot monitoring, qualitative compliance tests, precise monitoring tests, circulation volumes, and port data. | Modelled conditionally and run on synthetic data |
| Q4 | Combine the intake and contaminant models to evaluate national, regional, or food-specific safety and warn about possible events. | Modelled conditionally and run on synthetic data |
| Q5 | Estimate a nonnegative contaminant distribution, or at least its mean, when much of the information is left-censored and only values above a threshold plus limited below-threshold information are available. | Censored likelihood supplied and tested |
| Q6 | Reconcile two unpaired samples whose surveyed people and sampled foods are generally not matched. | Conditional-stratum integration supplied |
| Q7 | Reconcile inconsistent food classifications, including historical classifications that cannot be changed. | Mass-conserving crosswalk supplied |
| Q8 | Use selected provincial/municipal monitoring samples to infer a national or pooled population even when the source distributions may differ. | Survey-weight/transport and sensitivity route supplied |
| Q9 | Improve the precision of the all-resident `99.999%` right quantile of daily intake. | Tail-estimation protocol supplied; synthetic run shows material remaining uncertainty |

The statement presents Q5-Q8 as examples of urgent theoretical questions rather than a closed, exhaustively numbered list. This run treats them as explicit requested modelling issues because the source asks for detailed analysis of them.

## Evaluation and risk facts

- **PROBLEM_GIVEN_FACT — evaluation object:** the safety state of a country, region, food category, or population-pollutant combination at a time.
- **PROBLEM_GIVEN_FACT — risk object:** an individual's daily intake of a specified contaminant, treated as a random variable across residents/days.
- **PROBLEM_GIVEN_FACT — primary statistic:** not only the mean but the `99.999%` right quantile of daily contaminant intake.
- **PROBLEM_GIVEN_FACT — decision comparison:** compare that quantile with a safety standard set by the responsible authority. A clearly smaller quantile supports a safety conclusion under the model and evidence.
- **PROBLEM_GIVEN_FACT — high-exposure focus:** high-exposure residents matter more than the population mean alone.
- **PROBLEM_GIVEN_FACT — decision subject:** food-hygiene safety authorities and leaders using the result for monitoring and decisions.
- **PROBLEM_GIVEN_FACT — warning output:** the risk model should warn about possible food-safety events.
- **PROBLEM_GIVEN_FACT — contaminants mentioned as examples:** lead, cadmium, organophosphorus compounds, and organochlorine compounds. The statement does not supply measurements for them.

## Indicator and output requirements

| Question | Source answer |
|---|---|
| Does the problem require a ranking of alternatives? | No. It asks for safety evaluation and warning, not an ordered league table. |
| Does it require high/medium/low grading? | No named grade system is supplied. |
| Does it require an indicator system? | No MCDM indicator system is required. It requires linked intake, contamination, and risk models. |
| Does it require an improvement to an existing model? | Yes in substance: fix nondetect handling, mismatched samples/categories, extreme-tail precision, incomplete regional coverage, and black-box uncertainty. |
| Does it require theoretical analysis? | Yes, explicitly. |
| Does it require instance calculation? | It says models require data but no large-scale data are available during the contest; teams are expected to solve the difficulty creatively. No official numerical dataset is supplied. |
| Are external data allowed or required? | Operational use requires surveys, monitoring, circulation/port/emission information, and authority standards. This run did not acquire them because the statement supplies none and a modern replacement would be temporally inconsistent. |

## Data facts

- **PROBLEM_GIVEN_FACT:** a total-diet survey would weigh household food stocks at two visits and register unweighed consumption such as vegetables and water.
- **PROBLEM_GIVEN_FACT:** only thousands to at most tens of thousands of households can be sampled among hundreds of millions; the statement describes the sampling fraction as around `1/10,000` or smaller.
- **PROBLEM_GIVEN_FACT:** detailed food categories can number in the thousands, creating a workload/precision trade-off.
- **PROBLEM_GIVEN_FACT:** routine monitoring includes random low-rate sampling, seasonality, regionality, diversity, qualitative compliance tests, higher-precision monitoring tests, circulation volumes, and port tests.
- **PROBLEM_GIVEN_FACT:** roughly `2%` occasional spot-check data are suggested as possible information about the below-threshold part of a distribution.
- **PROBLEM_GIVEN_FACT:** nondetects must not all be silently set to zero.
- **PROBLEM_GIVEN_FACT:** intake and contamination samples are unpaired and their taxonomies may differ.
- **PROBLEM_GIVEN_FACT:** large-scale data are not provided with the question.
- **SOURCE ASSERTION REQUIRING VALIDATION:** the statement calls contaminant content “left-skewed” while also describing a nonnegative distribution whose density decreases as content grows. Skew direction is not inferred from this wording; it must be checked in data. A lognormal is only a run-specific scenario, not a source fact.

## Units and definitions

The statement does not give the units of food intake, contaminant concentration, body weight, daily intake, or safety standard. The model therefore keeps units symbolic:

- `I_j`: food-category intake, mass food/person-day;
- `C_jc`: contaminant concentration, mass contaminant/mass food;
- `D_c = Σ_j I_j C_jc`: contaminant mass/person-day;
- optionally `D_c / W` when the authority standard is mass/kg-body-weight/day;
- `T_c`: authority threshold in the same unit as `D_c`;
- `ρ_c = q_0.99999(D_c) / T_c`: dimensionless threshold ratio.

## Modelling assumptions introduced by this run

- **MODELING_ASSUMPTION:** the synthetic experiment uses three canonical food groups and lognormal intake/concentration variables solely to test the workflow.
- **MODELING_ASSUMPTION:** intake and contamination are conditionally independent within a declared demographic-region-season stratum when no paired data exist.
- **MODELING_ASSUMPTION:** a constant detection limit is used within each synthetic food group.
- **MODELING_ASSUMPTION:** monitoring quality uncertainty is reported separately and cannot compensate for a hard exposure violation.
- **MODELING_ASSUMPTION:** secondary triage, when requested, is lexicographic after the hard gate; it is not a safety probability.

All synthetic values are `SCENARIO_ASSUMED`. None describes actual 2007 or modern Chinese food safety.
