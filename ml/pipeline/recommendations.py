"""Explainable resource-optimization recommendations for WASTESENSE."""

import math
from collections.abc import Mapping
from typing import Any


def _finite_nonnegative(value: Any, name: str) -> float:
    """Validate a finite, non-negative numeric input."""
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric, not boolean.")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric.") from exc
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{name} must be finite and non-negative.")
    return result


def _optional_score(value: Any, name: str) -> float | None:
    if value is None:
        return None
    score = _finite_nonnegative(value, name)
    if score > 1:
        raise ValueError(f"{name} must be between 0 and 1.")
    return score


def generate_recommendations(input_data: Mapping[str, Any]) -> dict[str, Any]:
    """Generate cautious recommendations from actual and expected resources.

    Required inputs:
        actual_cpu, expected_cpu, actual_memory, expected_memory

    Optional inputs:
        waste_score: normalized score between 0 and 1
        persistence_detected: boolean
        root_cause_hypotheses: list of descriptive strings

    Recommendations are advisory. They do not execute changes or guarantee
    safe capacity reclamation, performance improvement, or financial savings.
    """
    if not isinstance(input_data, Mapping):
        raise TypeError("input_data must be a mapping.")

    required = (
        "actual_cpu",
        "expected_cpu",
        "actual_memory",
        "expected_memory",
    )
    missing = [key for key in required if key not in input_data]
    if missing:
        raise ValueError(f"Missing required inputs: {missing}")

    actual_cpu = _finite_nonnegative(input_data["actual_cpu"], "actual_cpu")
    expected_cpu = _finite_nonnegative(input_data["expected_cpu"], "expected_cpu")
    actual_memory = _finite_nonnegative(
        input_data["actual_memory"], "actual_memory"
    )
    expected_memory = _finite_nonnegative(
        input_data["expected_memory"], "expected_memory"
    )
    waste_score = _optional_score(input_data.get("waste_score"), "waste_score")

    persistence = input_data.get("persistence_detected", False)
    if not isinstance(persistence, bool):
        raise ValueError("persistence_detected must be a boolean.")

    hypotheses = input_data.get("root_cause_hypotheses", [])
    if not isinstance(hypotheses, list) or any(
        not isinstance(item, str) or not item.strip() for item in hypotheses
    ):
        raise ValueError("root_cause_hypotheses must be a list of non-empty strings.")

    resources = {
        "cpu": (actual_cpu, expected_cpu),
        "memory": (actual_memory, expected_memory),
    }
    recommendations = []

    for resource, (actual, expected) in resources.items():
        signed_excess = actual - expected
        positive_excess = max(0.0, signed_excess)
        if positive_excess <= 0:
            continue

        reasons = [
            f"Observed {resource} usage exceeds expected usage by "
            f"{positive_excess:.6g} in the input measurement scale."
        ]
        if persistence:
            reasons.append("Waste persistence was reported by the caller.")
        if waste_score is not None:
            reasons.append(f"Supplied waste score: {waste_score:.3f}.")

        if persistence and waste_score is not None and waste_score >= 0.7:
            priority = "high"
        elif persistence or (waste_score is not None and waste_score >= 0.4):
            priority = "medium"
        else:
            priority = "low"

        if resource == "cpu":
            action = (
                "Review workload CPU demand, recent workload changes, and "
                "CPU allocation. Consider a controlled rightsizing trial "
                "only after checking peak demand and performance objectives."
            )
        else:
            action = (
                "Review workload memory demand, peak memory use, and "
                "allocation. Consider a controlled rightsizing trial only "
                "after checking memory pressure and out-of-memory risk."
            )

        recommendations.append({
            "resource": resource,
            "priority": priority,
            "action": action,
            "observed_actual": actual,
            "expected": expected,
            "positive_excess": positive_excess,
            "reasons": reasons,
            "root_cause_hypotheses": list(hypotheses),
            "confidence": "advisory; not a calibrated probability",
            "estimated_savings": None,
            "requires_human_review": True,
        })

    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(
        key=lambda item: (
            priority_order[item["priority"]],
            -item["positive_excess"],
            item["resource"],
        )
    )

    return {
        "status": "recommendations_generated",
        "recommendation_count": len(recommendations),
        "recommendations": recommendations,
        "limitations": [
            "Recommendations are advisory and do not execute infrastructure changes.",
            "Positive excess does not prove safely reclaimable capacity.",
            "Priority rules are heuristics, not a learned or calibrated risk model.",
            "Root-cause hypotheses are unconfirmed and are not treated as causal proof.",
            "No power, energy, or monetary savings are estimated.",
            "Human review and controlled rollout are required before optimization.",
        ],
    }

def generate_recommendations_from_analysis(
    input_data: Mapping[str, Any],
    waste_analysis: Mapping[str, Any],
    persistence_analysis: Mapping[str, Any] | None = None,
    root_cause_analysis: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Integrate Phase 6 waste analysis and Phase 7 intelligence outputs."""
    if not isinstance(waste_analysis, Mapping):
        raise ValueError("waste_analysis must be a mapping.")

    score_result = waste_analysis.get("waste_score")
    if not isinstance(score_result, Mapping) or "score" not in score_result:
        raise ValueError("waste_analysis must contain a waste_score mapping.")

    score_100 = _finite_nonnegative(score_result["score"], "waste score")
    if score_100 > 100:
        raise ValueError("waste score must not exceed 100.")

    persistence_detected = False
    if persistence_analysis is not None:
        if not isinstance(persistence_analysis, Mapping):
            raise ValueError("persistence_analysis must be a mapping.")
        persistence_detected = persistence_analysis.get(
            "persistence_detected", False
        )
        if not isinstance(persistence_detected, bool):
            raise ValueError("persistence_detected must be a boolean.")

    hypotheses = []
    if root_cause_analysis is not None:
        if not isinstance(root_cause_analysis, Mapping):
            raise ValueError("root_cause_analysis must be a mapping.")
        items = root_cause_analysis.get("hypotheses", [])
        if not isinstance(items, list):
            raise ValueError("root-cause hypotheses must be a list.")
        for item in items:
            if not isinstance(item, Mapping):
                raise ValueError("Each root-cause hypothesis must be a mapping.")
            description = item.get("hypothesis")
            if not isinstance(description, str) or not description.strip():
                raise ValueError("Each hypothesis must have a non-empty description.")
            hypotheses.append(description.strip())

        if root_cause_analysis.get("root_cause_confirmed", False) is not False:
            raise ValueError(
                "Root-cause confirmation is not supported by this integration."
            )

    recommendation_input = dict(input_data)
    recommendation_input["waste_score"] = score_100 / 100.0
    recommendation_input["persistence_detected"] = persistence_detected
    recommendation_input["root_cause_hypotheses"] = hypotheses

    result = generate_recommendations(recommendation_input)
    result["integration"] = {
        "status": "phase6_phase7_integration_completed",
        "waste_analysis_status": waste_analysis.get("status"),
        "persistence_status": (
            None if persistence_analysis is None
            else persistence_analysis.get("status")
        ),
        "root_cause_status": (
            None if root_cause_analysis is None
            else root_cause_analysis.get("status")
        ),
        "waste_score_conversion": "score on 0-100 scale divided by 100",
        "root_cause_confirmed": False,
    }
    return result
