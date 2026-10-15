from pathlib import Path
import json
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/training/machine_resource_features_final_power_pdu.csv"
MODEL_DIR = ROOT / "ml/artifacts/models"
META_DIR = ROOT / "ml/artifacts/metadata"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
META_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
FEATURES = [
    "active_tasks", "cpu_capacity", "memory_capacity",
    "avg_priority", "max_priority", "elapsed_minutes",
    "trace_hour", "day_of_trace", "is_peak_period",
]
TARGETS = ["actual_cpu", "actual_memory", "actual_power"]
REQUIRED = ["timestamp_us", "machine_id", "pdu"] + FEATURES + TARGETS

def metrics(y, pred):
    return {
        "mae": float(mean_absolute_error(y, pred)),
        "rmse": float(np.sqrt(mean_squared_error(y, pred))),
        "r2": float(r2_score(y, pred)),
    }

def make_model(iterations=1200):
    return CatBoostRegressor(
        iterations=iterations,
        depth=7,
        learning_rate=0.04,
        loss_function="RMSE",
        eval_metric="RMSE",
        task_type="GPU",
        devices="0",
        random_seed=SEED,
        allow_writing_files=False,
        verbose=100,
    )

def time_split(frame, timestamps):
    n = len(timestamps)
    train_end = int(n * 0.70)
    val_end = int(n * 0.85)
    train_times = set(timestamps[:train_end])
    val_times = set(timestamps[train_end:val_end])
    test_times = set(timestamps[val_end:])
    return (
        frame[frame.timestamp_us.isin(train_times)].copy(),
        frame[frame.timestamp_us.isin(val_times)].copy(),
        frame[frame.timestamp_us.isin(test_times)].copy(),
    )

def train_one(name, frame, target, features, categorical=None):
    categorical = categorical or []
    timestamps = np.sort(frame.timestamp_us.unique())
    train, val, test = time_split(frame, timestamps)

    if min(len(train), len(val), len(test)) == 0:
        raise ValueError(f"{name}: empty chronological split")

    X_train, y_train = train[features], train[target]
    X_val, y_val = val[features], val[target]
    X_test, y_test = test[features], test[target]

    model = make_model()
    model.fit(
        X_train, y_train,
        cat_features=categorical,
        eval_set=(X_val, y_val),
        early_stopping_rounds=100,
        verbose=100,
    )

    best_iteration = model.get_best_iteration()
    iterations = max(50, best_iteration + 1) if best_iteration >= 0 else 1200

    # Refit on train + validation after selecting iteration count.
    trainval = pd.concat([train, val], ignore_index=True)
    final_model = make_model(iterations=iterations)
    final_model.fit(
        trainval[features],
        trainval[target],
        cat_features=categorical,
        verbose=100,
    )

    pred = final_model.predict(X_test)
    baseline_value = float(y_train.mean())
    baseline_pred = np.full(len(y_test), baseline_value)

    model_path = MODEL_DIR / f"expected_resource_{name}.cbm"
    final_model.save_model(str(model_path))

    result = {
        "target": target,
        "prediction_level": "PDU-time" if name == "power" else "machine-time",
        "features": features,
        "categorical_features": categorical,
        "best_iteration_on_validation": int(best_iteration),
        "final_iterations": int(iterations),
        "split_rows": {
            "train": int(len(train)),
            "validation": int(len(val)),
            "test": int(len(test)),
        },
        "test_metrics": metrics(y_test, pred),
        "mean_baseline_test_metrics": metrics(y_test, baseline_pred),
        "model_path": str(model_path.relative_to(ROOT)),
    }

    predictions = pd.DataFrame({
        "timestamp_us": test.timestamp_us.to_numpy(),
        "actual": y_test.to_numpy(),
        "predicted": pred,
        "baseline_predicted": baseline_pred,
    })
    if "pdu" in test.columns:
        predictions["pdu"] = test["pdu"].to_numpy()
    if "machine_id" in test.columns:
        predictions["machine_id"] = test["machine_id"].to_numpy()

    predictions.to_csv(
        META_DIR / f"{name}_test_predictions.csv", index=False
    )
    return result

def main():
    if not DATA.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA}")

    df = pd.read_csv(DATA)
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError(f"Required columns missing: {missing}")

    df = df.sort_values(["timestamp_us", "machine_id"]).reset_index(drop=True)

    numeric = FEATURES + TARGETS
    if not np.isfinite(df[numeric].to_numpy(dtype=float)).all():
        raise ValueError("Non-finite values found in features or targets")
    if (df[["cpu_capacity", "memory_capacity"]] <= 0).any().any():
        raise ValueError("Non-positive resource capacity found")
    if (df["active_tasks"] < 0).any():
        raise ValueError("Negative active task count found")

    timestamps = np.sort(df.timestamp_us.unique())
    if len(timestamps) < 20:
        raise ValueError("Insufficient time buckets for chronological splitting")

    print(f"Dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Unique time buckets: {len(timestamps)}")
    print("GPU training: CatBoost task_type=GPU")
    print("Features exclude actual resource targets and target-derived features.")

    results = {}
    results["cpu"] = train_one(
        "cpu", df, "actual_cpu", FEATURES
    )
    results["memory"] = train_one(
        "memory", df, "actual_memory", FEATURES
    )

    # Power is shared by each PDU/time bucket. Aggregate workload first
    # so repeated machine rows do not count as independent power labels.
    group_keys = ["timestamp_us", "pdu"]
    power = df.groupby(group_keys, as_index=False).agg(
        actual_power=("actual_power", "first"),
        power_values=("actual_power", "nunique"),
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

    if (power["power_values"] != 1).any():
        raise ValueError("Inconsistent power labels within a PDU/time group")

    power_features = [
        "machine_count", "total_active_tasks", "total_cpu_capacity",
        "total_memory_capacity", "mean_avg_priority", "max_priority",
        "elapsed_minutes", "trace_hour", "day_of_trace", "is_peak_period",
    ]
    pdu_dummies = pd.get_dummies(power["pdu"], prefix="pdu", dtype=int)
    power = pd.concat([power, pdu_dummies], axis=1)
    power_features += list(pdu_dummies.columns)

    # Reuse the common trainer with the aggregated PDU/time table.
    # machine_id is not required at this level.
    power_result = train_one(
        "power", power, "actual_power", power_features
    )
    power_result["prediction_level"] = "PDU-time"
    power_result["aggregation"] = "timestamp_us + pdu"
    results["power"] = power_result

    report = {
        "dataset": str(DATA.relative_to(ROOT)),
        "random_seed": SEED,
        "split_method": "chronological 70% train / 15% validation / 15% test",
        "gpu": "CatBoost GPU (RTX 4050 verified separately)",
        "results": results,
    }
    report_path = META_DIR / "expected_resource_model_metrics.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n=== FINAL HELD-OUT TEST RESULTS ===")
    for name, result in results.items():
        print(f"\n{name.upper()}")
        print("Test:", json.dumps(result["test_metrics"], indent=2))
        print("Mean baseline:", json.dumps(
            result["mean_baseline_test_metrics"], indent=2
        ))
        print("Model:", result["model_path"])

    print(f"\nMetrics saved to: {report_path}")
    print("Training completed. Review metrics before accepting models.")

if __name__ == "__main__":
    main()
