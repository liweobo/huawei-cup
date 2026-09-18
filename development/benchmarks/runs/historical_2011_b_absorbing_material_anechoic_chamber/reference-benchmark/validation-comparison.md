# Validation comparison

| reference | internal physical checks | numerical checks | independent validation | assessment |
|---|---|---|---|---|
| B10145011 | qualitative energy/reflection reasoning | limited visible convergence | none | internally plausible, weak external validation |
| B10247007 | energy conservation explicitly discussed | wall partition 2..30 and convergence reported | none | strongest among coupled wall models |
| B10286058 | ray/radiosity consistency | progressive refinement and tables | none | plausible, but closure depends on tip-entry assumption |
| B10293022 | symmetry and balance implied | no strong grid study located | none | result usable as a scenario, not certified |
| B10319002 | two Q2 models compared | model comparison, no independent data | none | honest about agreement but no independent validation |
| B10386003 | image-path and power attenuation | 600-reflection cutoff stated, no truncation study | none | model error and truncation error not separated |
| B10699002 | geometry/Huygens comparison | explicit mesh refinement table to 0.5 m | none | best numerical-verification evidence; model discrepancy remains |
| B10699008 | angle and power recurrence | limited quantitative grid evidence | none | good regime separation, incomplete convergence evidence |
| B90002072 | view-factor energy structure | integration/grid convergence not demonstrated | none | physically interpretable but weak numerical evidence |
| B90005018 | direct/one-bounce sanity | no all-reflection verification | none | explicitly partial Q2 mechanism |
| B90045020 | rho=0 and rho=1 limiting weighted construction | Monte Carlo result shown; statistical error not fully reported | none | model-form sensitivity is visible, validation remains internal |

No reference has independent chamber measurements. The papers mainly validate with symmetry, energy balance, limiting cases, table/plot behavior and numerical refinement. Therefore “excellent” status does not convert these calculations into experimental validation.

The Blind Run's convergence and physical checks are stronger than several references, but its external validity is equally limited and its result must remain conditional on the chosen mechanism.
