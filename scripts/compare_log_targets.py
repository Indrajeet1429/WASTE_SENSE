from pathlib import Path
import json
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/training/machine_resource_features_final_power_pdu.csv"
OUT = ROOT / "ml/artifacts/metadata/log_target_validation_comparison.json"

SEED = 42
FEATURES = [
    "active_tasks", "cpu_capacity", "memory_capacity",
    "avg_priority", "max_priority", "elapsed_minutes",
    "trace_hour", "day_of_trace", "is_peak_period",
]

def make_model():
    return CatBoostRegressor(
        iterations=1200,
        depth=7,
        learning_rate=0.04,
        loss_function="RMSE",
        eval_metric="RMSE",
        task_type="GPU",
        devices="0",
        random_seed=SEED,
        allow_writing_files=False,
        verbose=200,
    )

def calculate_metrics(actual, predicted):
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted)),
    }

def main():
    if not DATA.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA}")

    df = pd.read_csv(DATA)
    df = df.sort_values(["timestamp_us", "machine_id"]).reset_index(drop=True)

    required = FEATURES + ["timestamp_us", "actual_cpu", "actual_memory"]
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    timestamps = np.sort(df["timestamp_us"].unique())
    n = len(timestamps)
    train_end = int(n * 0.70)
    val_end = int(n * 0.85)

    train = df[df["timestamp_us"].isin(timestamps[:train_end])]
    val = df[df["timestamp_us"].isin(timestamps[train_end:val_end])]

    if train.empty or val.empty:
        raise ValueError("Training or validation split is empty")

    results = {
        "experiment": "ordinary versus log1p target",
        "selection_data": "chronological validation only",
        "test_set_used": False,
        "train_timestamps": int(train["timestamp_us"].nunique()),
        "validation_timestamps": int(val["timestamp_us"].nunique()),
        "targets": {},
    }

    for target in ["actual_cpu", "actual_memory"]:
        y_train = train[target].to_numpy(dtype=float)
        y_val = val[target].to_numpy(dtype=float)

        if (y_train < 0).any() or (y_val < 0).any():
            raise ValueError(f"{target} contains negative values")

        X_train = train[FEATURES]
        X_val = val[FEATURES]
        baseline = np.full(len(y_val), y_train.mean())

        print(f"\n{'=' * 60}\nTARGET: {target}")
        print("Training ordinary-target model...")
        ordinary = make_model()
        ordinary.fit(
            X_train, y_train,
            eval_set=(X_val, y_val),
            early_stopping_rounds=100,
            verbose=200,
        )
        ordinary_pred = np.maximum(ordinary.predict(X_val), 0)

        print("Training log1p-target model...")
        log_model = make_model()
        log_model.fit(
            X_train, np.log1p(y_train),
            eval_set=(X_val, np.log1p(y_val)),
            early_stopping_rounds=100,
            verbose=200,
        )
        log_pred = np.maximum(np.expm1(log_model.predict(X_val)), 0)

        target_results = {
            "mean_baseline": calculate_metrics(y_val, baseline),
            "ordinary_target": {
                **calculate_metrics(y_val, ordinary_pred),
                "best_iteration": int(ordinary.get_best_iteration()),
            },
            "log1p_target": {
                **calculate_metrics(y_val, log_pred),
                "best_iteration": int(log_model.get_best_iteration()),
            },
        }
        results["targets"][target] = target_results

        print("\nVALIDATION METRICS (original target scale)")
        print(json.dumps(target_results, indent=2))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nComparison saved to: {OUT}")
    print("No existing model, test prediction, or test metric file was changed.")

if __name__ == "__main__":
    main()
