
"""PDU-time power inference for WASTESENSE."""

from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "ml/artifacts/models/expected_resource_power.cbm"

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


def predict_expected_power(input_data: Mapping[str, Any]) -> dict:
    """Predict power for one aggregated PDU-time workload."""
    if not isinstance(input_data, Mapping):
        raise TypeError("input_data must be a dictionary-like mapping.")

    missing = [name for name in POWER_FEATURES if name not in input_data]
    if missing:
        raise ValueError(f"Missing power features: {missing}")

    pdu = input_data.get("pdu")
    if pdu not in {"pdu10", "pdu6", "pdu7", "pdu8", "pdu9"}:
        raise ValueError("pdu must be one of pdu10, pdu6, pdu7, pdu8, pdu9.")

    row = pd.DataFrame(
        [{name: input_data[name] for name in POWER_FEATURES}],
        columns=POWER_FEATURES,
    ).apply(pd.to_numeric, errors="raise")

    values = row.to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Power features must be finite numbers.")

    for name in ("machine_count", "total_cpu_capacity", "total_memory_capacity"):
        if float(row.iloc[0][name]) <= 0:
            raise ValueError(f"{name} must be positive.")

    if float(row.iloc[0]["total_active_tasks"]) < 0:
        raise ValueError("total_active_tasks cannot be negative.")

    # Ensure PDU indicators agree with the supplied PDU identity.
    for name in ("pdu_pdu10", "pdu_pdu6", "pdu_pdu7", "pdu_pdu8", "pdu_pdu9"):
        expected = int(name == f"pdu_{pdu}")
        if float(row.iloc[0][name]) != expected:
            raise ValueError(f"{name} does not match pdu={pdu}.")

    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Power model not found: {MODEL_PATH}")

    model = CatBoostRegressor()
    model.load_model(str(MODEL_PATH))

    if list(model.feature_names_) != POWER_FEATURES:
        raise ValueError("Stored power model feature names do not match.")

    prediction = float(model.predict(row)[0])
    if not np.isfinite(prediction):
        raise ValueError("Power model returned a non-finite prediction.")

    return {
        "status": "prediction_completed",
        "prediction_level": "PDU-time",
        "pdu": pdu,
        "expected_power": max(0.0, prediction),
        "model": "CatBoost",
    }
