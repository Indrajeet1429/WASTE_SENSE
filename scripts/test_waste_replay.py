from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.pipeline.waste_replay import replay_observations


def must_raise(function, *args, **kwargs):
    try:
        function(*args, **kwargs)
    except (ValueError, TypeError):
        return
    raise AssertionError(f"Expected validation error from {function.__name__}")


observations = [
    {
        "machine_id": 2,
        "timestamp_us": 200,
        "actual_cpu": 0.08,
        "expected_cpu": 0.05,
        "actual_memory": 0.04,
        "expected_memory": 0.03,
    },
    {
        "machine_id": 1,
        "timestamp_us": 100,
        "actual_cpu": 0.02,
        "expected_cpu": 0.05,
        "actual_memory": 0.02,
        "expected_memory": 0.03,
    },
]

result = replay_observations(observations, optimization_fraction=0.5)
assert result["status"] == "waste_replay_completed"
assert result["observation_count"] == 2
assert result["observations"][0]["timestamp_us"] == 100
assert abs(result["totals"]["cpu_positive_excess"] - 0.03) < 1e-12
assert abs(result["totals"]["hypothetical_cpu_reduction"] - 0.015) < 1e-12
assert abs(result["totals"]["memory_positive_excess"] - 0.01) < 1e-12
assert abs(result["totals"]["hypothetical_memory_reduction"] - 0.005) < 1e-12
assert result["realized_savings"] is None

zero = replay_observations(observations, optimization_fraction=0)
assert zero["totals"]["hypothetical_cpu_reduction"] == 0
assert zero["totals"]["hypothetical_memory_reduction"] == 0

full = replay_observations(observations, optimization_fraction=1)
assert abs(
    full["totals"]["hypothetical_cpu_reduction"]
    - full["totals"]["cpu_positive_excess"]
) < 1e-12

must_raise(replay_observations, [], optimization_fraction=0.5)
must_raise(replay_observations, observations, optimization_fraction=-0.1)
must_raise(replay_observations, observations, optimization_fraction=1.1)
must_raise(
    replay_observations,
    [dict(observations[0], actual_cpu=float("nan"))],
    optimization_fraction=0.5,
)
must_raise(
    replay_observations,
    [dict(observations[0], timestamp_us=100.5)],
    optimization_fraction=0.5,
)
must_raise(
    replay_observations,
    [observations[0], dict(observations[0])],
    optimization_fraction=0.5,
)
must_raise(
    replay_observations,
    [{"machine_id": 1}],
    optimization_fraction=0.5,
)

print("PASS: Chronological replay and excess calculations")
print("PASS: Zero, partial, and full hypothetical reductions")
print("PASS: Invalid fraction and numeric input validation")
print("PASS: Duplicate, missing-field, and timestamp validation")
print("ALL WASTE REPLAY TESTS PASSED")
