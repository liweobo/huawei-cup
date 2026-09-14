# Small-Sample Imbalanced Binary Classification

Read this reference when a labelled binary task has a small sample, an
uneven class distribution, or a high-accuracy/minority-recall warning. It is
an evaluation and model-selection protocol, not a promise that a particular
algorithm will improve the score.

## Audit And Baseline

1. Record the two class counts, prevalence, majority/minority labels and
   imbalance ratio. A nearly balanced task is still valid; do not block it
   merely because this reference was activated.
2. Evaluate the always-majority baseline before fitting a candidate. Accuracy
   is descriptive only and cannot be the primary selection criterion when the
   minority class matters.
3. Compare regularized logistic regression and a small number of materially
   different, capacity-controlled candidates. Where supported, compare
   unweighted and `class_weight="balanced"` variants under the same protocol.
   Shallow tree/boosting or a linear/RBF SVM can be candidates when their
   assumptions and sample size justify them; do not dump a large model list.

## Metrics And Validation

Report, at minimum, ROC-AUC and PR-AUC when probabilities/scores exist,
minority recall, precision, F1, Macro F1, Balanced Accuracy and specificity.
Include positive prevalence so PR-AUC has a baseline context. For probability
tasks also report Brier score and state whether calibration was checked.

When no stronger group or time structure applies, use repeated stratified
validation. Report each metric's mean, standard deviation, median and range;
the fold values remain part of the evidence. If entities, time, sites or other
groups define dependence, use the stronger group/time splitter instead of
silently using stratification.

Preprocessing, imputation, scaling, feature selection, PCA and resampling
must be fitted inside the cross-validation pipeline. Split first; never run
SMOTE or any other resampling on the full data before the split.

## Probability And Thresholds

Keep the probability model and the decision threshold separate. Select a
threshold only with validation (or an inner validation loop), then freeze it
before evaluating an untouched test set. Test labels, all-data labels and a
threshold chosen after inspecting test outcomes are leakage. Report the
recall/precision/specificity/F1 trade-off rather than presenting a threshold
as universally optimal.

The reusable checks and summaries are in
[`scripts/metrics.py`](../scripts/metrics.py):

- `class_distribution_summary()` and `majority_class_baseline()`;
- `binary_probability_metrics()` and `evaluate_binary_threshold()`;
- `select_classification_threshold()` (validation-only);
- `repeated_stratified_cv_metrics()`;
- `feature_sample_size_check()`;
- `validate_resampling_scope()` and `validate_preprocessing_scope()`;
- `imbalanced_model_selection_check()`.

## Selection Gate

A candidate with high accuracy and zero minority recall is not a
`VALID_FINAL_MODEL` when the minority class is part of the task, even if its
accuracy exceeds the majority baseline. A model must be compared with the
majority baseline using the task-relevant operating point and the full metric
set. Do not claim an improvement without a same-data, same-split, same-metric
comparison.

Before selecting a final model, answer explicitly:

1. What is the majority baseline?
2. What are CV ROC-AUC and PR-AUC relative to positive prevalence?
3. What are minority Recall, Precision, F1 and Balanced Accuracy?
4. How variable are these metrics across folds/repeats?
5. Is feature dimensionality plausible for the sample size, and is there
   evidence of severe overfitting?
6. If probabilities are required, what does Brier/calibration evidence show?
7. What threshold was used, where was it selected and what trade-off does it
   implement?
8. Why is the selected model preferable after stability, interpretability and
   complexity are considered?

## Evidence Fields

For an imbalanced binary experiment, preserve only the additional provenance
needed for the decision:

```yaml
class_distribution:
  majority_count:
  minority_count:
  positive_prevalence:
imbalance_ratio:
majority_baseline:
validation_protocol:
threshold_selection_scope: validation
primary_metrics: [PR-AUC, Balanced Accuracy, Positive Class Recall]
```

These fields supplement the existing Experiment Record; they do not replace
run binding, temporal availability checks or the Active Evidence Set.
