# Phase 9: Optimization Recommendations

## 1. Objective

Phase 9 converts resource-usage analysis into explainable, advisory optimization recommendations. It identifies CPU or memory usage above expected levels and suggests actions for human review.

## 2. Implementation

Main module: `ml/pipeline/recommendations.py`

Main functions:
- `generate_recommendations(input_data)`: Generates recommendations from actual and expected CPU and memory usage.
- `generate_recommendations_from_analysis(input_data, waste_analysis, persistence_analysis=None, root_cause_analysis=None)`: Integrates recommendations with earlier waste-analysis and intelligence outputs.

Tests:
- `scripts/test_recommendations.py`
- `scripts/test_phase9_integration.py`

## 3. Required Inputs

The recommendation engine requires:
- `actual_cpu`: observed CPU usage.
- `expected_cpu`: expected CPU usage.
- `actual_memory`: observed memory usage.
- `expected_memory`: expected memory usage.

Optional inputs:
- `waste_score`: normalized heuristic score from 0 to 1.
- `persistence_detected`: Boolean indicating whether persistence was detected.
- `root_cause_hypotheses`: descriptive, unconfirmed hypotheses.

Numeric resource inputs must be finite and non-negative. Invalid values are rejected.

## 4. Recommendation Logic

A CPU or memory recommendation is produced when actual usage exceeds expected usage.

Positive excess is calculated as:

`positive_excess = max(0, actual_usage - expected_usage)`

The heuristic priority rules are:
- **High:** persistence is detected and normalized waste score is at least 0.7.
- **Medium:** persistence is detected, or normalized waste score is at least 0.4, when the high-priority condition does not apply.
- **Low:** neither medium nor high conditions apply.

The waste-analysis score uses a 0–100 scale. Integration converts it to the recommendation engine's 0–1 scale by dividing by 100.

These thresholds are heuristics, not calibrated probabilities or a learned risk model.

## 5. Output

The result contains:
- Overall generation status.
- Recommendation count.
- Recommended resource.
- Heuristic priority.
- Suggested review action.
- Actual, expected, and positive-excess measurements.
- Supporting reasons and root-cause hypotheses.
- A human-review requirement.
- Explicit limitations.

Recommendations are ordered deterministically by priority, positive excess, and resource name.

## 6. Integration

Phase 9 consumes waste analysis from Phase 6 and intelligence outputs from Phase 7. It accepts persistence information and unconfirmed root-cause hypotheses.

Phase 8 provides separate savings-estimation and replay functionality. Those outputs must not be interpreted as proof that savings have been realized. The current recommendation interface does not itself calculate monetary or power savings.

## 7. Safety and Limitations

- Recommendations do not execute infrastructure changes.
- Positive excess does not prove that capacity can safely be reclaimed.
- Root-cause hypotheses are not confirmed causes.
- Priority is heuristic and is not a calibrated probability.
- Estimated or hypothetical reductions are not realized savings.
- No monetary or power savings are claimed by this recommendation engine.
- Human review, workload peak analysis, performance checks, and controlled rollout are required before optimization.

## 8. Test Results

The following test modules passed during Phase 9 development:
- `scripts.test_recommendations`
- `scripts.test_phase9_integration`
- `scripts.test_savings_estimator`
- `scripts.test_waste_replay`
- `scripts.test_phase8_integration`

These results demonstrate that the reported test cases passed in the development environment. They do not guarantee correctness for every possible workload or prove real-world resource savings.

## 9. Phase 9 Completion Criteria

- Recommendation engine implemented.
- Input validation and deterministic ordering covered by tests.
- Phase 6 and Phase 7 integration covered by tests.
- Human review and uncertainty represented in outputs.
- Phase 8 regression tests passed.
- Documentation prepared.

## 10. Handoff to Phase 10

Phase 10 should evaluate the complete ML workflow using suitable datasets, metrics, baselines, and reproducible experiments. Evaluation should distinguish predictive performance from heuristic waste detection and hypothetical savings. Report limitations and avoid claiming production readiness without deployment-relevant evidence.
