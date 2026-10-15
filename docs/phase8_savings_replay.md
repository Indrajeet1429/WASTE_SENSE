# Phase 8: Savings Estimation and Waste Replay

## 1. Purpose

Phase 8 provides transparent estimates of potential CPU and memory excess and a historical replay of hypothetical optimization scenarios. It does not execute changes to workloads or infrastructure.

## 2. Modules

### Savings estimator

File: `ml/pipeline/savings_estimator.py`

Main functions:

- `estimate_resource_savings(actual, expected, resource)`: calculates signed excess and positive excess for one resource.
- `estimate_savings(input_data)`: calculates CPU and memory estimates from a mapping containing `actual_cpu`, `expected_cpu`, `actual_memory`, and `expected_memory`.

For each resource:

- Signed excess = actual value - expected value.
- Potential positive excess = max(0, signed excess).

Negative signed excess means actual usage is below expected usage. Positive excess indicates a potential opportunity, not proof that the resource is unnecessary or safely reclaimable.

The estimator does not calculate realized savings. Power savings are explicitly marked as not estimated.

### Waste Replay

File: `ml/pipeline/waste_replay.py`

Main function:

`replay_observations(observations, optimization_fraction=...)`

Each observation must contain:

- `machine_id`
- `timestamp_us`
- `actual_cpu`
- `expected_cpu`
- `actual_memory`
- `expected_memory`

The observations must be a non-empty sequence. Numeric resource values must be finite and non-negative. Timestamps must be non-negative integers. Duplicate machine-and-timestamp observations are rejected.

The optimization fraction must be between 0 and 1, inclusive:

- `0`: no hypothetical reduction.
- `0.5`: hypothetically reduces 50% of positive excess.
- `1`: hypothetically reduces 100% of positive excess.

The fraction applies only to positive CPU and memory excess. Replay observations are sorted by timestamp, with a string representation of the machine ID used as the secondary sort key.

## 3. Replay calculations

For each observation:

- CPU positive excess = max(0, actual CPU - expected CPU).
- Memory positive excess = max(0, actual memory - expected memory).
- Hypothetical reduction = positive excess × optimization fraction.
- Hypothetical value after reduction = actual value - hypothetical reduction.

The result includes per-observation calculations and totals for positive excess and hypothetical reductions.

## 4. Integration

The savings estimator and Waste Replay are separate functions. Their results can be compared to verify calculation consistency.

Example:

```python
from ml.pipeline.savings_estimator import estimate_savings
from ml.pipeline.waste_replay import replay_observations

observation = {
    "machine_id": 101,
    "timestamp_us": 1000,
    "actual_cpu": 0.08,
    "expected_cpu": 0.05,
    "actual_memory": 0.04,
    "expected_memory": 0.03,
}

estimate = estimate_savings(observation)

replay = replay_observations(
    [observation],
    optimization_fraction=0.5,
)

print(estimate["cpu"]["potential_excess"])
print(replay["totals"]["hypothetical_cpu_reduction"])