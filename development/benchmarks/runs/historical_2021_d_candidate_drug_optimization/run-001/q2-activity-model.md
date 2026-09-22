# Q2 Activity Model

The modeled target is the supplied continuous pIC50. IC50 in nM is derived only for output with `10^(9-pIC50)`. Candidate comparison uses identical rows, five outer folds, metrics, and fold-local descriptor policy. Mean and median dummy regressors establish location baselines; Ridge is the regularized linear candidate; Extra Trees is the materially different nonlinear candidate. Ridge searches four alpha values. Extra Trees searches two feature fractions and two leaf sizes. Each search uses three inner folds.

Model family selection minimizes mean outer-fold RMSE, with Ridge preferred only if candidate RMSEs are within 0.02. Extra Trees wins clearly. The final model is re-fit on all 1,974 legal training compounds only after this choice freezes. Prediction uncertainty is the standard deviation of the five outer-fold models' test predictions.

The selected trees show a large train/validation gap (mean train R² 0.993 versus validation R² 0.729). This is retained as an overfitting warning; the reported performance and Q4 uncertainty use held-out evidence, never training fit.
