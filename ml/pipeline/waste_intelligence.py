"""Waste fingerprint utilities for WASTESENSE Phase 7."""

import math
from collections.abc import Mapping
from typing import Any


def _finite_nonnegative(value: Any, name: str) -> float:
    """Validate a finite, non-negative numeric value."""
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric.") from exc

    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{name} must be finite and non-negative.")

    return result


def build_waste_fingerprint(
    waste_analysis: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build a descriptive fingerprint from Phase 6 waste-analysis output.

    This function classifies the relative CPU and memory excess signals.
    It does not establish causation, persistence, or guaranteed savings.
    """
    if not isinstance(waste_analysis, Mapping):
        raise ValueError("waste_analysis must be a mapping.")

    cpu_result = waste_analysis.get("cpu")
    memory_result = waste_analysis.get("memory")
    score_result = waste_analysis.get("waste_score")

    if not isinstance(cpu_result, Mapping):
        raise ValueError("waste_analysis must contain CPU results.")
    if not isinstance(memory_result, Mapping):
        raise ValueError("waste_analysis must contain memory results.")
    if not isinstance(score_result, Mapping):
        raise ValueError("waste_analysis must contain a waste score.")

    cpu_signal = _finite_nonnegative(
        cpu_result.get("normalized_adjusted_excess"),
        "CPU normalized adjusted excess",
    )
    memory_signal = _finite_nonnegative(
        memory_result.get("normalized_adjusted_excess"),
        "Memory normalized adjusted excess",
    )
    score = _finite_nonnegative(
        score_result.get("score"),
        "Waste score",
    )

    if score > 100:
        raise ValueError("Waste score must not exceed 100.")

    severity = waste_analysis.get("severity")
    if not isinstance(severity, str) or not severity.strip():
        raise ValueError("Waste analysis must contain a severity label.")

    dominance_ratio = 1.5

    if cpu_signal == 0 and memory_signal == 0:
        fingerprint_type = "no_adjusted_excess"
        dominant_resource = "none"
        balance_ratio = None
        interpretation = (
            "No CPU or memory excess remains above the provisional "
            "uncertainty thresholds."
        )
    elif memory_signal == 0 or (
        cpu_signal > 0 and cpu_signal / max(memory_signal, 1e-300)
        > dominance_ratio
    ):
        fingerprint_type = "cpu_dominant"
        dominant_resource = "cpu"
        balance_ratio = (
            cpu_signal / memory_signal if memory_signal > 0 else None
        )
        interpretation = (
            "The adjusted CPU excess signal is substantially larger "
            "than the memory signal."
        )
    elif cpu_signal == 0 or (
        memory_signal > 0 and memory_signal / max(cpu_signal, 1e-300)
        > dominance_ratio
    ):
        fingerprint_type = "memory_dominant"
        dominant_resource = "memory"
        balance_ratio = (
            memory_signal / cpu_signal if cpu_signal > 0 else None
        )
        interpretation = (
            "The adjusted memory excess signal is substantially larger "
            "than the CPU signal."
        )
    else:
        fingerprint_type = "balanced_cpu_memory_excess"
        dominant_resource = "both"
        balance_ratio = max(cpu_signal, memory_signal) / min(
            cpu_signal, memory_signal
        )
        interpretation = (
            "CPU and memory adjusted excess signals are of similar "
            "magnitude."
        )

    return {
        "status": "fingerprint_generated",
        "fingerprint_type": fingerprint_type,
        "dominant_resource": dominant_resource,
        "signals": {
            "cpu_normalized_adjusted_excess": cpu_signal,
            "memory_normalized_adjusted_excess": memory_signal,
        },
        "balance_ratio": balance_ratio,
        "dominance_ratio_threshold": dominance_ratio,
        "waste_score": score,
        "severity": severity,
        "method": "Relative comparison of Phase 6 uncertainty-adjusted excess",
        "interpretation": interpretation,
        "limitations": [
            "The fingerprint is descriptive, not a confirmed root cause.",
            "A zero adjusted signal does not prove that resource waste is absent.",
            "Classification depends on provisional uncertainty and ratio thresholds.",
            "Persistence must be assessed using time-ordered observations.",
        ],
    }


def detect_waste_persistence(
    observations: list[Mapping[str, Any]],
    *,
    max_gap_seconds: float,
    score_threshold: float = 5.0,
    minimum_observations: int = 3,
) -> dict[str, Any]:
    """
    Detect consecutive above-threshold waste scores for one machine.

    Each observation must contain timestamp_us and waste_score.
    The caller must supply observations for a single machine only.
    Gaps exceeding max_gap_seconds break a streak.
    """
    if not isinstance(observations, list) or not observations:
        raise ValueError("observations must be a non-empty list.")

    max_gap = _finite_nonnegative(max_gap_seconds, "max_gap_seconds")
    if max_gap <= 0:
        raise ValueError("max_gap_seconds must be positive.")

    threshold = _finite_nonnegative(score_threshold, "score_threshold")
    if threshold > 100:
        raise ValueError("score_threshold must not exceed 100.")

    if (
        isinstance(minimum_observations, bool)
        or not isinstance(minimum_observations, int)
        or minimum_observations < 2
    ):
        raise ValueError("minimum_observations must be an integer >= 2.")

    normalized = []
    for index, item in enumerate(observations):
        if not isinstance(item, Mapping):
            raise ValueError(f"Observation {index} must be a mapping.")

        timestamp = _finite_nonnegative(
            item.get("timestamp_us"), f"observations[{index}].timestamp_us"
        )
        score = _finite_nonnegative(
            item.get("waste_score"), f"observations[{index}].waste_score"
        )

        if score > 100:
            raise ValueError(
                f"observations[{index}].waste_score must not exceed 100."
            )

        normalized.append({
            "timestamp_us": timestamp,
            "waste_score": score,
        })

    normalized.sort(key=lambda item: item["timestamp_us"])

    timestamps = [item["timestamp_us"] for item in normalized]
    if len(set(timestamps)) != len(timestamps):
        raise ValueError("Duplicate timestamps are not allowed.")

    streak = []
    streaks = []

    for item in normalized:
        qualifies = item["waste_score"] >= threshold

        if not qualifies:
            if streak:
                streaks.append(streak)
                streak = []
            continue

        if streak:
            gap_seconds = (
                item["timestamp_us"] - streak[-1]["timestamp_us"]
            ) / 1_000_000

            if gap_seconds > max_gap:
                streaks.append(streak)
                streak = []

        streak.append(item)

    if streak:
        streaks.append(streak)

    longest = max(streaks, key=len, default=[])
    latest = streak if streak else []

    def summarize(items):
        if not items:
            return {
                "observation_count": 0,
                "duration_seconds": 0.0,
                "start_timestamp_us": None,
                "end_timestamp_us": None,
                "persistent": False,
            }

        return {
            "observation_count": len(items),
            "duration_seconds": (
                items[-1]["timestamp_us"] - items[0]["timestamp_us"]
            ) / 1_000_000,
            "start_timestamp_us": items[0]["timestamp_us"],
            "end_timestamp_us": items[-1]["timestamp_us"],
            "persistent": len(items) >= minimum_observations,
        }

    latest_summary = summarize(latest)
    longest_summary = summarize(longest)

    return {
        "status": "persistence_analysis_completed",
        "score_threshold": threshold,
        "max_gap_seconds": max_gap,
        "minimum_observations": minimum_observations,
        "latest_streak": latest_summary,
        "longest_streak": longest_summary,
        "persistence_detected": latest_summary["persistent"],
        "streak_count": len(streaks),
        "limitations": [
            "Input observations must belong to one machine.",
            "Persistence is based on heuristic waste scores, not proof of waste.",
            "The score threshold and time-gap limit are configurable heuristics.",
            "Elapsed time between observations does not establish continuous waste.",
        ],
    }





def analyze_root_cause(
    waste_analysis: Mapping[str, Any],
    workload_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate evidence-based root-cause hypotheses from waste signals.

    Results are hypotheses, not proof of causation.
    Optional context is used only when explicitly supplied.
    """
    fingerprint = build_waste_fingerprint(waste_analysis)
    context = {} if workload_context is None else workload_context

    if not isinstance(context, Mapping):
        raise ValueError("workload_context must be a mapping.")

    hypotheses = []
    evidence = []

    cpu_signal = fingerprint["signals"]["cpu_normalized_adjusted_excess"]
    memory_signal = fingerprint["signals"]["memory_normalized_adjusted_excess"]

    if fingerprint["fingerprint_type"] == "no_adjusted_excess":
        hypotheses.append({
            "hypothesis": "No excess above the configured noise floors",
            "confidence": "not_assessed",
            "reason": (
                "Neither CPU nor memory has positive adjusted excess "
                "under the current heuristic thresholds."
            ),
        })
    elif fingerprint["fingerprint_type"] == "cpu_dominant":
        hypotheses.append({
            "hypothesis": "CPU-dominant excess",
            "confidence": "signal_supported",
            "reason": (
                "The normalized, uncertainty-adjusted CPU excess "
                "is substantially larger than the memory excess."
            ),
        })
    elif fingerprint["fingerprint_type"] == "memory_dominant":
        hypotheses.append({
            "hypothesis": "Memory-dominant excess",
            "confidence": "signal_supported",
            "reason": (
                "The normalized, uncertainty-adjusted memory excess "
                "is substantially larger than the CPU excess."
            ),
        })
    else:
        hypotheses.append({
            "hypothesis": "Combined CPU and memory excess",
            "confidence": "signal_supported",
            "reason": (
                "Both resources have adjusted excess of similar magnitude."
            ),
        })

    evidence.append({
        "observation": "CPU normalized adjusted excess",
        "value": cpu_signal,
        "source": "Phase 6 waste analysis",
    })
    evidence.append({
        "observation": "Memory normalized adjusted excess",
        "value": memory_signal,
        "source": "Phase 6 waste analysis",
    })

    context_rules = [
        (
            "active_tasks",
            "Workload task count is available",
            "The supplied active task count describes workload quantity, "
            "but does not establish whether the workload needed the resources.",
        ),
        (
            "workload_stability_15min",
            "Workload stability feature is available",
            "This feature may help assess workload variation; it does not "
            "prove that excess resource usage is unnecessary.",
        ),
        (
            "headroom_imbalance",
            "Resource headroom imbalance feature is available",
            "This feature may help describe an imbalance between CPU and "
            "memory headroom, but does not establish its cause.",
        ),
        (
            "cpu_memory_utilization_gap",
            "CPU-memory utilization gap is available",
            "This gap describes a difference between resource utilization "
            "levels and is not independently evidence of waste.",
        ),
    ]

    for field, label, interpretation in context_rules:
        if field not in context:
            continue

        value = context[field]
        try:
            numeric_value = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field} must be a finite number.") from exc

        if not math.isfinite(numeric_value):
            raise ValueError(f"{field} must be a finite number.")

        evidence.append({
            "observation": label,
            "field": field,
            "value": numeric_value,
            "interpretation": interpretation,
        })

    return {
        "status": "root_cause_hypotheses_generated",
        "fingerprint_type": fingerprint["fingerprint_type"],
        "waste_score": fingerprint["waste_score"],
        "severity": fingerprint["severity"],
        "hypotheses": hypotheses,
        "evidence": evidence,
        "root_cause_confirmed": False,
        "limitations": [
            "These are rule-based hypotheses, not confirmed causal explanations.",
            "CPU and memory model accuracy is limited.",
            "Workload context is optional and is not inferred when missing.",
            "Confirming root causes requires additional evidence or controlled experiments.",
        ],
    }
