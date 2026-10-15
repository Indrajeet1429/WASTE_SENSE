from pathlib import Path
import sys
import math

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.pipeline.savings_estimator import estimate_savings
from ml.pipeline.waste_replay import replay_observations


def check(condition, message):
    if not condition:
        raise AssertionError(message)
    print(f"PASS: {message}")


def main():
    # 1. Estimate potential CPU and memory excess for one observation.
    observation = {
        "machine_id": 101,
        "timestamp_us": 1000,
        "actual_cpu": 0.08,
        "expected_cpu": 0.05,
        "actual_memory": 0.04,
        "expected_memory": 0.03,
    }

    savings = estimate_savings(observation)

    check(
        savings["status"] == "potential_savings_estimated",
        "Savings estimation completed",
    )
    check(
        math.isclose(savings["cpu"]["potential_excess"], 0.03),
        "CPU potential excess is correct",
    )
    check(
        math.isclose(savings["memory"]["potential_excess"], 0.01),
        "Memory potential excess is correct",
    )
    check(
        savings["power"]["status"] == "not_estimated",
        "Power savings are not falsely estimated",
    )

    # 2. Replay the same observation with a 50% hypothetical reduction.
    replay = replay_observations(
        [observation],
        optimization_fraction=0.5,
    )

    check(
        replay["status"] == "waste_replay_completed",
        "Waste Replay completed",
    )
    check(
        replay["observation_count"] == 1,
        "Replay includes the expected observation",
    )
    check(
        math.isclose(
            replay["totals"]["hypothetical_cpu_reduction"],
            savings["cpu"]["potential_excess"] * 0.5,
        ),
        "Replay CPU reduction agrees with savings estimate",
    )
    check(
        math.isclose(
            replay["totals"]["hypothetical_memory_reduction"],
            savings["memory"]["potential_excess"] * 0.5,
        ),
        "Replay memory reduction agrees with savings estimate",
    )

    # 3. Confirm that hypothetical reductions are not actual savings.
    check(
        savings["cpu"]["realized_savings"] is None
        and savings["memory"]["realized_savings"] is None
        and replay["realized_savings"] is None,
        "Realized savings remain unclaimed",
    )

    # 4. Check that below-expected usage does not create a reduction.
    below_expected = {
        "machine_id": 102,
        "timestamp_us": 2000,
        "actual_cpu": 0.02,
        "expected_cpu": 0.05,
        "actual_memory": 0.01,
        "expected_memory": 0.03,
    }
    no_excess_replay = replay_observations(
        [below_expected],
        optimization_fraction=0.5,
    )

    check(
        no_excess_replay["totals"]["hypothetical_cpu_reduction"] == 0.0
        and no_excess_replay["totals"]["hypothetical_memory_reduction"] == 0.0,
        "Below-expected usage produces no hypothetical reduction",
    )

    print(
        "\nPASS: Phase 8 savings and replay integration checks completed. "
        "This test verifies calculation consistency, not real-world savings."
    )


if __name__ == "__main__":
    main()
