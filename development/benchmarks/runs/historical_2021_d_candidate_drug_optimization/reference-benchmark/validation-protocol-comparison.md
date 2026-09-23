# Validation Protocol Comparison

## Protocol matrix

| evidence item | Frozen run | R1 | R2 | R3 | R4 | R5 |
|---|---|---|---|---|---|---|
| data/source audit | yes | partial | partial | partial | partial | partial |
| explicit baseline | yes | no | no | no | partial: linear candidate, no baseline contract | no |
| held-out/outer validation | repeated outer folds | random 80/20 | random 80/20 | random 80/20 | random 75/25 | random 80/20 |
| fold-safe feature selection | yes | no | no | no | no | no |
| independent hyperparameter selection | yes | unclear | no: test reused | unclear | no: test-informed feature choice | unclear |
| imbalance-aware metrics | yes | partial | no | no | partial | partial |
| validation-only threshold | yes | no/unstated | no | no/unstated | no/unstated | fixed/default |
| calibration evidence | yes | no | no | no | no | no |
| Q4 predictive uncertainty | yes | no | no | no | no | no |
| optimization feasibility/domain | finite candidates + empirical AD | marginal ranges only | marginal ranges only | marginal ranges only | marginal ranges only | marginal ranges + limited integer rules |
| independent result reconstruction | yes | no | no | no | no | no |
| explicit claim boundary | yes | weak | weak | partial | weak | weak |

## Reference protocol classifications

- R1: `TRAIN_TEST_SPLIT` with CV tuning; `FULL_DATA` supervised selection precedes evaluation.
- R2: `TRAIN_TEST_SPLIT` plus K-fold work; selection precedes evaluation and test outcomes influence decisions.
- R3: `TRAIN_TEST_SPLIT`; repeated selection does not become nested validation.
- R4: `TRAIN_TEST_SPLIT` plus GridSearchCV; test-set permutation importance and pre-split SMOTE create leakage risks.
- R5: `TRAIN_TEST_SPLIT` plus K-fold work; appendix code fits supervised selectors before CV.

None is `NESTED_CV` for the complete selection-and-tuning pipeline. Reported folds therefore cannot be interpreted as leakage-free estimates of each paper's entire workflow.

## Evidence-chain assessment

The frozen run uniquely combines source audit, baseline, outer held-out validation, fold-safe preprocessing/selection, threshold discipline, uncertainty, feasibility, independent reconstruction, and a bounded final claim. Reference methods may be competitive algorithms, but their evidence chains do not support direct numerical superiority claims.
