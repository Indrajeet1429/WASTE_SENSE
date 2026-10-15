from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor

ROOT = Path(".")
DATA = ROOT / "data/processed/training/machine_resource_features_final_power_pdu.csv"
MODEL_DIR = ROOT / "ml/artifacts/models"

df = pd.read_csv(DATA)
features = [
    "active_tasks", "cpu_capacity", "memory_capacity",
    "avg_priority", "max_priority", "elapsed_minutes",
    "trace_hour", "day_of_trace", "is_peak_period",
]

models = {
    "CPU": ("expected_resource_cpu.cbm", features, df[features].head(10)),
    "Memory": ("expected_resource_memory.cbm", features, df[features].head(10)),
}

power_features = [
    "machine_count", "total_active_tasks", "total_cpu_capacity",
    "total_memory_capacity", "mean_avg_priority", "max_priority",
    "elapsed_minutes", "trace_hour", "day_of_trace", "is_peak_period",
]

power = df.groupby(["timestamp_us", "pdu"], as_index=False).agg(
    machine_count=("machine_id", "nunique"),
    total_active_tasks=("active_tasks", "sum"),
    total_cpu_capacity=("cpu_capacity", "sum"),
    total_memory_capacity=("memory_capacity", "sum"),
    mean_avg_priority=("avg_priority", "mean"),
    max_priority=("max_priority", "max"),
    elapsed_minutes=("elapsed_minutes", "first"),
    trace_hour=("trace_hour", "first"),
    day_of_trace=("day_of_trace", "first"),
    is_peak_period=("is_peak_period", "first"),
)
dummies = pd.get_dummies(power["pdu"], prefix="pdu", dtype=int)
power = pd.concat([power, dummies], axis=1)
power_features += list(dummies.columns)
models["Power"] = (
    "expected_resource_power.cbm",
    power_features,
    power[power_features].head(10),
)

for name, (filename, expected_features, sample) in models.items():
    path = MODEL_DIR / filename
    print(f"\n{name}: {path}")

    if not path.exists():
        print("FAIL: Model file missing")
        continue

    try:
        model = CatBoostRegressor()
        model.load_model(str(path))
        actual_features = model.feature_names_

        if actual_features != expected_features:
            print("FAIL: Feature names/order do not match")
            print("Expected:", expected_features)
            print("Loaded:", actual_features)
            continue

        predictions = np.asarray(model.predict(sample), dtype=float)
        valid = len(predictions) == len(sample) and np.isfinite(predictions).all()

        print("Loaded: PASS")
        print("Feature count:", len(actual_features))
        print("Prediction shape:", predictions.shape)
        print("Finite predictions:", bool(valid))
        print("Prediction range:", float(predictions.min()), "to", float(predictions.max()))
        print("Prediction test:", "PASS" if valid else "FAIL")
    except Exception as exc:
        print("FAIL:", repr(exc))
