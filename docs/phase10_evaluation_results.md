# Phase 10: Consolidated Evaluation Results

## 1. Scope

This report consolidates the available resource-prediction metrics, baseline comparisons, and functional test outcomes recorded during Phase 10. Results describe the evaluated test samples and do not guarantee production performance.

## 2. Resource Prediction Metrics

| Resource | Test rows | MAE | RMSE | R-squared |
|---|---:|---:|---:|---:|
| CPU | 8,963 | 0.008016 | 0.014278 | 0.145897 |
| Memory | 8,963 | 0.003832 | 0.007861 | 0.036059 |
| Power | 85 | 0.005033 | 0.006490 | 0.899127 |

Metrics use the target scales in the existing prediction files. MAE and RMSE are not percentages unless the target scale makes them so.

## 3. Baseline Comparison

| Resource | Model MAE | Baseline MAE | MAE improvement | RMSE improvement |
|---|---:|---:|---:|---:|
| CPU | 0.008016 | 0.008006 | -0.12% | 8.06% |
| Memory | 0.003832 | 0.003837 | 0.14% | 2.08% |
| Power | 0.005033 | 0.037970 | 86.74% | 84.95% |

Positive improvement indicates lower error than the baseline. Negative improvement indicates higher error.

### Interpretation

- CPU: mixed results. MAE is slightly worse than baseline, while RMSE and R-squared are better.
- Memory: small improvements over baseline; practical value remains uncertain.
- Power: substantial improvement over baseline on the available 85-row test set. The limited sample size requires caution.

The CPU and memory R-squared values indicate limited explanatory predictive performance. These results should be reported honestly rather than treated as uniformly successful models.

## 4. Waste Detection and Intelligence

The following functional test modules passed:
- `scripts.test_waste_detection`
- `scripts.test_waste_intelligence`

Reported checks covered excess and normalization, uncertainty adjustment, score capping, severity boundaries, end-to-end scenarios, fingerprint classification, persistence behavior, root-cause hypothesis handling, and invalid inputs.

These tests establish expected behavior for the tested cases. Real-world precision, recall, and F1 have not been established by these results because a trustworthy labelled evaluation set has not been demonstrated.

## 5. Recommendations, Savings, and Replay

The following test modules passed:
- `scripts.test_recommendations`
- `scripts.test_phase9_integration`
- `scripts.test_savings_estimator`
- `scripts.test_waste_replay`
- `scripts.test_phase8_integration`

Reported checks covered recommendation priorities, input validation, human-review requirements, root-cause uncertainty, potential CPU and memory excess, chronological replay, hypothetical reductions, and consistency between savings estimates and replay outputs.

Potential or hypothetical reductions are not realized savings. No unsupported power or monetary savings are claimed.

## 6. Limitations and Risks

1. CPU and memory prediction metrics show limited improvement in some measures.
2. The power test sample contains 85 rows, limiting confidence in broad generalization.
3. Waste-detection functional tests do not substitute for labelled real-world evaluation.
4. Root-cause outputs are hypotheses, not confirmed causal explanations.
5. Recommendation priorities are heuristic rather than calibrated risk probabilities.
6. Savings and replay calculations do not establish actual operational or financial savings.
7. The reported results do not by themselves establish production readiness.

## 7. Evaluation Conclusion

The available tests support functional consistency in the evaluated scenarios. Power prediction is promising on the available test sample. CPU and memory results are mixed or weak and should remain visible as limitations.

The results do not justify claiming that every model is highly accurate or that WASTESENSE has demonstrated real-world savings. Further validation using suitable labelled data and deployment-relevant measurements would be needed for those claims.

## 8. Reproducibility

The reported regression test modules are:
- `scripts.test_waste_detection`
- `scripts.test_waste_intelligence`
- `scripts.test_recommendations`
- `scripts.test_phase9_integration`
- `scripts.test_savings_estimator`
- `scripts.test_waste_replay`
- `scripts.test_phase8_integration`

The regression runs reported during Phase 10 passed. The metric values above were calculated from the existing prediction CSVs; this report does not claim that models were retrained.

## 9. Handoff

Proceed to Step 6 after reviewing the evaluation record and completing the required final documentation and handoff. Earlier phases remain locked unless a concrete defect is identified.
