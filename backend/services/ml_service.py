"""
WASTESENSE ML Service
Member 5 — FastAPI + ML Integration

Connects the FastAPI backend to Member 1's workload inference pipeline.
"""

from importlib import import_module
from typing import Any, Mapping


class MLServiceError(Exception):
    """Base exception for ML service failures."""


class MLModelUnavailableError(MLServiceError):
    """Raised when the ML pipeline or trained models are unavailable."""


class MLInputError(MLServiceError):
    """Raised when workload input is invalid."""


def _validate_workload(input_data: Mapping[str, Any]) -> dict[str, Any]:
    """Validate workload fields before calling the ML pipeline."""

    if not isinstance(input_data, Mapping):
        raise MLInputError("Workload input must be a JSON object.")

    required_fields = (
        "machine_id",
        "timestamp",
        "active_tasks",
        "cpu_capacity",
        "memory_capacity",
        "actual_cpu",
        "actual_memory",
    )

    missing_fields = [
        field
        for field in required_fields
        if field not in input_data or input_data[field] is None
    ]

    if missing_fields:
        raise MLInputError(
            f"Missing required workload fields: {', '.join(missing_fields)}"
        )

    validated = dict(input_data)

    for field in (
        "active_tasks",
        "cpu_capacity",
        "memory_capacity",
        "actual_cpu",
        "actual_memory",
    ):
        value = validated[field]

        if isinstance(value, bool):
            raise MLInputError(f"'{field}' must be a numeric value.")

        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise MLInputError(f"'{field}' must be a numeric value.") from exc

        if number != number or number in (float("inf"), float("-inf")):
            raise MLInputError(f"'{field}' must be finite.")

        validated[field] = number

    if validated["active_tasks"] < 0:
        raise MLInputError("'active_tasks' cannot be negative.")

    if validated["cpu_capacity"] <= 0:
        raise MLInputError("'cpu_capacity' must be greater than zero.")

    if validated["memory_capacity"] <= 0:
        raise MLInputError("'memory_capacity' must be greater than zero.")

    for field in ("actual_cpu", "actual_memory"):
        if validated[field] < 0:
            raise MLInputError(f"'{field}' cannot be negative.")

    for field in ("machine_id", "timestamp"):
        if not isinstance(validated[field], str) or not validated[field].strip():
            raise MLInputError(f"'{field}' must be a non-empty string.")

    return validated


def analyze_workload(input_data: Mapping[str, Any]) -> dict[str, Any]:
    """
    Validate input and call Member 1's analyze_workload inference function.

    ML source code must be present in the current Python environment.
    Trained model files must also be available for actual predictions.
    """

    validated_data = _validate_workload(input_data)

    try:
        inference_module = import_module("ml.pipeline.inference")
    except (ImportError, ModuleNotFoundError) as exc:
        raise MLModelUnavailableError(
            "The ML inference module is unavailable in the current checkout. "
            "Integrate Member 1's ml/pipeline modules before running analysis."
        ) from exc

    inference_function = getattr(inference_module, "analyze_workload", None)

    if not callable(inference_function):
        raise MLModelUnavailableError(
            "Member 1's inference module does not expose analyze_workload()."
        )

    try:
        result = inference_function(validated_data)
    except FileNotFoundError as exc:
        raise MLModelUnavailableError(
            "Required trained ML model files are missing. "
            "Obtain the model artifacts from Member 1 before running predictions."
        ) from exc
    except (ValueError, KeyError, TypeError) as exc:
        raise MLInputError(f"The ML pipeline rejected the workload: {exc}") from exc

    if not isinstance(result, dict):
        raise MLServiceError("The ML pipeline returned an invalid result.")

    return result