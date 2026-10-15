"""Transparent potential resource-savings estimates for WASTESENSE."""

import math
from typing import Any, Mapping


def _validate_resource_value(value: Any, name: str) -> float:
    """Convert a resource value to a finite, non-negative float."""
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a numeric resource value.")

    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric.") from exc

    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{name} must be finite and non-negative.")

    return result


def estimate_resource_savings(
    actual: Any,
    expected: Any,
    resource: str,
) -> dict[str, Any]:
    """Estimate positive excess without claiming it is recoverable savings."""
    if not isinstance(resource, str) or not resource.strip():
        raise ValueError("resource must be a non-empty string.")

    actual_value = _validate_resource_value(actual, "actual")
    expected_value = _validate_resource_value(expected, "expected")
    signed_excess = actual_value - expected_value
    positive_excess = max(0.0, signed_excess)

    return {
        "status": "potential_savings_estimated",
        "resource": resource.strip().lower(),
        "actual": actual_value,
        "expected": expected_value,
        "signed_excess": signed_excess,
        "potential_excess": positive_excess,
        "realized_savings": None,
        "unit": "same as input measurements; not inferred",
        "interpretation": (
            "Positive excess is a hypothetical opportunity, not proof "
            "that the resource can be safely reclaimed."
        ),
        "limitations": [
            "Expected usage depends on the predictive model's accuracy.",
            "Excess does not prove that usage is unnecessary.",
            "No conversion to energy, cost, or monetary savings is performed.",
            "Actual savings require a validated intervention and measurement.",
        ],
    }


def estimate_savings(input_data: Mapping[str, Any]) -> dict[str, Any]:
    """Estimate CPU and memory excess from actual and expected values."""
    if not isinstance(input_data, Mapping):
        raise TypeError("input_data must be a mapping.")

    required = ("actual_cpu", "expected_cpu", "actual_memory", "expected_memory")
    missing = [key for key in required if key not in input_data]
    if missing:
        raise ValueError(f"Missing required inputs: {missing}")

    cpu = estimate_resource_savings(
        input_data["actual_cpu"], input_data["expected_cpu"], "cpu"
    )
    memory = estimate_resource_savings(
        input_data["actual_memory"], input_data["expected_memory"], "memory"
    )

    return {
        "status": "potential_savings_estimated",
        "estimate_type": "hypothetical_resource_excess",
        "cpu": cpu,
        "memory": memory,
        "power": {
            "status": "not_estimated",
            "reason": (
                "Power savings require a separately validated PDU-time "
                "counterfactual and appropriate measurement assumptions."
            ),
        },
        "limitations": [
            "Estimates are not guarantees of reclaimable resources.",
            "CPU and memory estimates remain subject to model error.",
            "No energy or monetary savings are calculated.",
        ],
    }
