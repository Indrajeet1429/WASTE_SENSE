"""Historical resource replay for hypothetical WASTESENSE optimization."""

import math
from collections.abc import Mapping, Sequence
from typing import Any


def _finite_nonnegative(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric, not boolean.")

    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric.") from exc

    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{name} must be finite and non-negative.")

    return result


def _optimization_fraction(value: Any) -> float:
    if isinstance(value, bool):
        raise ValueError("optimization_fraction must be between 0 and 1.")

    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "optimization_fraction must be between 0 and 1."
        ) from exc

    if not math.isfinite(result) or not 0 <= result <= 1:
        raise ValueError("optimization_fraction must be between 0 and 1.")

    return result


def replay_observations(
    observations: Sequence[Mapping[str, Any]],
    *,
    optimization_fraction: float,
) -> dict[str, Any]:
    """Replay observations with an explicit hypothetical excess reduction.

    Required fields per observation:
        machine_id, timestamp_us, actual_cpu, expected_cpu,
        actual_memory, expected_memory.

    The optimization fraction applies only to positive excess. It does not
    establish that excess can safely be reclaimed in a real environment.
    """
    if isinstance(observations, (str, bytes)) or not isinstance(
        observations, Sequence
    ):
        raise ValueError("observations must be a sequence of mappings.")

    if not observations:
        raise ValueError("observations must not be empty.")

    fraction = _optimization_fraction(optimization_fraction)
    required = (
        "machine_id",
        "timestamp_us",
        "actual_cpu",
        "expected_cpu",
        "actual_memory",
        "expected_memory",
    )

    normalized = []
    seen = set()

    for index, observation in enumerate(observations):
        if not isinstance(observation, Mapping):
            raise ValueError(f"Observation {index} must be a mapping.")

        missing = [key for key in required if key not in observation]
        if missing:
            raise ValueError(
                f"Observation {index} is missing fields: {missing}"
            )

        machine_id = observation["machine_id"]
        if machine_id is None or isinstance(machine_id, bool):
            raise ValueError(f"Observation {index} has invalid machine_id.")

        timestamp = _finite_nonnegative(
            observation["timestamp_us"],
            f"observations[{index}].timestamp_us",
        )
        if not timestamp.is_integer():
            raise ValueError(
                f"Observation {index} timestamp_us must be an integer."
            )

        try:
            hash(machine_id)
        except TypeError as exc:
            raise ValueError(
                f"Observation {index} machine_id must be hashable."
            ) from exc

        key = (machine_id, int(timestamp))
        if key in seen:
            raise ValueError(
                f"Duplicate machine-time observation: {key!r}"
            )
        seen.add(key)

        actual_cpu = _finite_nonnegative(
            observation["actual_cpu"], f"observations[{index}].actual_cpu"
        )
        expected_cpu = _finite_nonnegative(
            observation["expected_cpu"], f"observations[{index}].expected_cpu"
        )
        actual_memory = _finite_nonnegative(
            observation["actual_memory"],
            f"observations[{index}].actual_memory",
        )
        expected_memory = _finite_nonnegative(
            observation["expected_memory"],
            f"observations[{index}].expected_memory",
        )

        cpu_excess = max(0.0, actual_cpu - expected_cpu)
        memory_excess = max(0.0, actual_memory - expected_memory)
        cpu_reduction = cpu_excess * fraction
        memory_reduction = memory_excess * fraction

        normalized.append({
            "machine_id": machine_id,
            "timestamp_us": int(timestamp),
            "actual_cpu": actual_cpu,
            "expected_cpu": expected_cpu,
            "cpu_positive_excess": cpu_excess,
            "hypothetical_cpu_reduction": cpu_reduction,
            "hypothetical_cpu_after": actual_cpu - cpu_reduction,
            "actual_memory": actual_memory,
            "expected_memory": expected_memory,
            "memory_positive_excess": memory_excess,
            "hypothetical_memory_reduction": memory_reduction,
            "hypothetical_memory_after": actual_memory - memory_reduction,
        })

    normalized.sort(key=lambda item: (item["timestamp_us"], str(item["machine_id"])))

    return {
        "status": "waste_replay_completed",
        "scenario": {
            "optimization_fraction": fraction,
            "basis": "Fraction of positive CPU and memory excess only",
            "type": "hypothetical_counterfactual",
        },
        "observation_count": len(normalized),
        "observations": normalized,
        "totals": {
            "cpu_positive_excess": sum(
                item["cpu_positive_excess"] for item in normalized
            ),
            "hypothetical_cpu_reduction": sum(
                item["hypothetical_cpu_reduction"] for item in normalized
            ),
            "memory_positive_excess": sum(
                item["memory_positive_excess"] for item in normalized
            ),
            "hypothetical_memory_reduction": sum(
                item["hypothetical_memory_reduction"] for item in normalized
            ),
        },
        "realized_savings": None,
        "limitations": [
            "Replay is hypothetical and does not execute resource changes.",
            "Positive excess does not prove safely reclaimable capacity.",
            "CPU and memory values retain their input measurement scales.",
            "No power, energy, or financial savings are inferred.",
            "Expected values inherit the limitations of their predictive models.",
        ],
    }
