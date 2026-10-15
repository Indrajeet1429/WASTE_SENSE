
"""Inference interface for WASTESENSE expected-resource models."""

from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from ml.pipeline.waste_detection import analyze_resource_waste
from ml.pipeline.savings_estimator import estimate_savings
from ml.pipeline.waste_intelligence import (
    build_waste_fingerprint,
    detect_waste_persistence,
    analyze_root_cause,
)
from ml.pipeline.recommendations import generate_recommendations_from_analysis
from ml.pipeline.waste_replay import replay_observations
from ml.pipeline.power_inference import predict_expected_power


ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "ml" / "artifacts" / "models"

RESOURCE_FEATURES = [
    "active_tasks",
    "cpu_capacity",
    "memory_capacity",
    "avg_priority",
    "max_priority",
    "elapsed_minutes",
    "trace_hour",
    "day_of_trace",
    "is_peak_period",
]

POWER_FEATURES = [
    "machine_count",
    "total_active_tasks",
    "total_cpu_capacity",
    "total_memory_capacity",
    "mean_avg_priority",
    "max_priority",
    "elapsed_minutes",
    "trace_hour",
    "day_of_trace",
    "is_peak_period",
    "pdu_pdu10",
    "pdu_pdu6",
    "pdu_pdu7",
    "pdu_pdu8",
    "pdu_pdu9",
]


def _load_model(filename: str, expected_features: list[str]) -> CatBoostRegressor:
    """Load a model and verify its stored feature names."""
    path = MODEL_DIR / filename

    if not path.is_file():
        raise FileNotFoundError(f"Model artifact not found: {path}")

    model = CatBoostRegressor()
    model.load_model(str(path))

    actual_features = list(model.feature_names_)
    if actual_features != expected_features:
        raise ValueError(
            f"Feature mismatch in {filename}. "
            f"Expected {expected_features}; found {actual_features}"
        )

    return model


def _validate_features(
    data: Mapping[str, Any],
    feature_names: list[str],
) -> pd.DataFrame:
    """Validate and arrange a single input row in model feature order."""
    missing = [name for name in feature_names if name not in data]
    if missing:
        raise ValueError(f"Missing required input features: {missing}")

    row = pd.DataFrame(
        [{name: data[name] for name in feature_names}],
        columns=feature_names,
    )

    row = row.apply(pd.to_numeric, errors="raise")

    values = row.to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Input features must all be finite numbers.")

    return row


def _predict_resource(
    model: CatBoostRegressor,
    data: Mapping[str, Any],
    target_name: str,
    actual_value: Any = None,
) -> dict[str, Any]:
    """Predict one resource and optionally compare with its actual value."""
    row = _validate_features(data, RESOURCE_FEATURES)

    if float(row.iloc[0]["cpu_capacity"]) <= 0:
        raise ValueError("cpu_capacity must be positive.")
    if float(row.iloc[0]["memory_capacity"]) <= 0:
        raise ValueError("memory_capacity must be positive.")
    if float(row.iloc[0]["active_tasks"]) < 0:
        raise ValueError("active_tasks cannot be negative.")

    prediction = float(model.predict(row)[0])

    result = {
        "resource": target_name,
        "expected": max(0.0, prediction),
        "actual": None,
        "excess": None,
        "model": "CatBoost",
    }

    if actual_value is not None:
        actual = float(actual_value)
        if not np.isfinite(actual) or actual < 0:
            raise ValueError(
                f"Actual {target_name} must be finite and non-negative."
            )

        result["actual"] = actual
        result["excess"] = actual - result["expected"]

    return result


def analyze_workload(input_data: Mapping[str, Any]) -> dict[str, Any]:
    """Predict expected resources and optionally analyze observed resource use."""
    if not isinstance(input_data, Mapping):
        raise TypeError("input_data must be a mapping, such as a dictionary.")

    cpu_model = _load_model("expected_resource_cpu.cbm", RESOURCE_FEATURES)
    memory_model = _load_model("expected_resource_memory.cbm", RESOURCE_FEATURES)

    cpu = _predict_resource(cpu_model, input_data, "cpu", input_data.get("actual_cpu"))
    memory = _predict_resource(
        memory_model, input_data, "memory", input_data.get("actual_memory")
    )

    result = {
        "status": "prediction_completed",
        "prediction_level": "machine-time",
        "resources": {"cpu": cpu, "memory": memory},
        "power": {
            "status": "not_predicted",
            "reason": (
                "Power prediction requires aggregated PDU-time features; "
                "this interface predicts resources at machine-time level."
            ),
        },
        "waste_analysis": {
            "status": "not_available",
            "reason": "Both actual_cpu and actual_memory are required.",
        },
        "waste_fingerprint": {"status": "not_available"},
        "persistence_analysis": {
            "status": "not_run",
            "reason": "Waste analysis and explicit observation history are required.",
        },
        "root_cause_analysis": {"status": "not_run"},
        "savings_estimate": {"status": "not_available"},
        "recommendations": {"status": "not_run"},
        "replay": {
            "status": "not_run",
            "reason": "Supply replay_observations and optimization_fraction to run a hypothetical replay.",
        },
    }

    if "power_input" in input_data:
        result["power"] = predict_expected_power(input_data["power_input"])

    if input_data.get("actual_cpu") is None or input_data.get("actual_memory") is None:
        return result

    waste = analyze_resource_waste(
        actual_cpu=cpu["actual"],
        expected_cpu=cpu["expected"],
        cpu_capacity=input_data["cpu_capacity"],
        actual_memory=memory["actual"],
        expected_memory=memory["expected"],
        memory_capacity=input_data["memory_capacity"],
    )
    result["waste_analysis"] = waste
    result["waste_fingerprint"] = build_waste_fingerprint(waste)

    savings_input = dict(input_data)
    savings_input["expected_cpu"] = cpu["expected"]
    savings_input["expected_memory"] = memory["expected"]
    result["savings_estimate"] = estimate_savings(savings_input)

    root_cause = analyze_root_cause(
        waste,
        workload_context=input_data.get("workload_context"),
    )
    result["root_cause_analysis"] = root_cause

    persistence = None
    if "persistence_observations" in input_data:
        if "max_gap_seconds" not in input_data:
            raise ValueError(
                "max_gap_seconds is required with persistence_observations."
            )
        persistence = detect_waste_persistence(
            input_data["persistence_observations"],
            max_gap_seconds=input_data["max_gap_seconds"],
            score_threshold=input_data.get("score_threshold", 5.0),
            minimum_observations=input_data.get("minimum_observations", 3),
        )
        result["persistence_analysis"] = persistence

    recommendation_input = dict(input_data)
    recommendation_input["expected_cpu"] = cpu["expected"]
    recommendation_input["expected_memory"] = memory["expected"]
    result["recommendations"] = generate_recommendations_from_analysis(
        recommendation_input,
        waste,
        persistence_analysis=persistence,
        root_cause_analysis=root_cause,
    )

    if "replay_observations" in input_data:
        if "optimization_fraction" not in input_data:
            raise ValueError(
                "optimization_fraction is required with replay_observations."
            )
        result["replay"] = replay_observations(
            input_data["replay_observations"],
            optimization_fraction=input_data["optimization_fraction"],
        )

    return result
