"""Waste detection utilities for WASTESENSE."""

import math
from typing import Any


def _finite_nonnegative(value: Any, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{name} must be finite and non-negative.")
    return result


def calculate_excess(actual: Any, expected: Any) -> dict[str, float]:
    """Calculate signed and positive excess in the original measurement scale."""
    actual_value = _finite_nonnegative(actual, "actual")
    expected_value = _finite_nonnegative(expected, "expected")
    signed_excess = actual_value - expected_value

    return {
        "actual": actual_value,
        "expected": expected_value,
        "signed_excess": signed_excess,
        "positive_excess": max(0.0, signed_excess),
    }


def normalize_excess(
    actual: Any,
    expected: Any,
    capacity: Any,
) -> dict[str, float]:
    """Normalize positive excess by the matching resource capacity."""
    capacity_value = float(capacity)
    if not math.isfinite(capacity_value) or capacity_value <= 0:
        raise ValueError("Capacity must be finite and positive.")

    result = calculate_excess(actual, expected)
    result["normalized_positive_excess"] = (
        result["positive_excess"] / capacity_value
    )
    return result


def calculate_uncertainty_adjusted_excess(
    actual: Any,
    expected: Any,
    capacity: Any,
    uncertainty_threshold: Any,
) -> dict[str, float]:
    """Apply a provisional noise floor before capacity normalization."""
    result = normalize_excess(actual, expected, capacity)
    threshold = _finite_nonnegative(
        uncertainty_threshold, "uncertainty_threshold"
    )

    adjusted = max(0.0, result["signed_excess"] - threshold)
    result["uncertainty_threshold"] = threshold
    result["adjusted_positive_excess"] = adjusted
    result["normalized_adjusted_excess"] = adjusted / float(capacity)
    return result


def calculate_waste_score(
    cpu_normalized_adjusted_excess: Any,
    memory_normalized_adjusted_excess: Any,
) -> dict[str, Any]:
    """
    Combine CPU and memory signals into a transparent heuristic score.

    Inputs must already be uncertainty-adjusted and capacity-normalized.
    The displayed score is capped at 100; uncapped values are preserved.
    """
    cpu = _finite_nonnegative(
        cpu_normalized_adjusted_excess,
        "cpu_normalized_adjusted_excess",
    )
    memory = _finite_nonnegative(
        memory_normalized_adjusted_excess,
        "memory_normalized_adjusted_excess",
    )

    raw_score = 100.0 * (cpu + memory) / 2.0
    score = min(100.0, raw_score)

    return {
        "status": "heuristic_score",
        "score": score,
        "raw_score": raw_score,
        "score_capped": raw_score > 100.0,
        "cpu_signal": cpu,
        "memory_signal": memory,
        "method": "Equal-weight mean of normalized adjusted excess",
        "interpretation": (
            "Heuristic indicator only; not proof of waste or guaranteed savings."
        ),
    }


def assign_severity(score: Any) -> dict[str, Any]:
    """Assign provisional severity to a heuristic waste score."""
    value = float(score)

    if not math.isfinite(value) or value < 0 or value > 100:
        raise ValueError("score must be finite and between 0 and 100.")

    if value == 0:
        severity = "none_detected"
    elif value < 5:
        severity = "low"
    elif value < 15:
        severity = "moderate"
    elif value < 30:
        severity = "high"
    else:
        severity = "critical"

    return {
        "score": value,
        "severity": severity,
        "thresholds_status": "provisional",
        "interpretation": (
            "Severity describes the heuristic score, not verified waste."
        ),
    }


# Provisional noise floors based on Phase 5 held-out MAE.
# These are heuristics, not calibrated confidence intervals.
CPU_UNCERTAINTY_THRESHOLD = 0.0080161673
MEMORY_UNCERTAINTY_THRESHOLD = 0.0038315691


def analyze_resource_waste(
    actual_cpu: Any,
    expected_cpu: Any,
    cpu_capacity: Any,
    actual_memory: Any,
    expected_memory: Any,
    memory_capacity: Any,
) -> dict[str, Any]:
    """Run the complete CPU/memory excess-to-severity pipeline."""
    cpu = calculate_uncertainty_adjusted_excess(
        actual=actual_cpu,
        expected=expected_cpu,
        capacity=cpu_capacity,
        uncertainty_threshold=CPU_UNCERTAINTY_THRESHOLD,
    )
    memory = calculate_uncertainty_adjusted_excess(
        actual=actual_memory,
        expected=expected_memory,
        capacity=memory_capacity,
        uncertainty_threshold=MEMORY_UNCERTAINTY_THRESHOLD,
    )

    score_result = calculate_waste_score(
        cpu["normalized_adjusted_excess"],
        memory["normalized_adjusted_excess"],
    )
    severity_result = assign_severity(score_result["score"])

    return {
        "status": "heuristic_analysis_completed",
        "cpu": cpu,
        "memory": memory,
        "waste_score": score_result,
        "severity": severity_result["severity"],
        "severity_thresholds_status": severity_result["thresholds_status"],
        "limitations": [
            "CPU and memory models have limited predictive performance.",
            "Uncertainty thresholds are provisional MAE-based noise floors.",
            "Severity boundaries are provisional engineering thresholds.",
            "Score is not proof of waste or a guarantee of savings.",
        ],
    }
