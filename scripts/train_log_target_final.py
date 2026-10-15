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
SEED = 42

FEATURES = [
    "active_tasks", "cpu_capacity", "memory_capacity",
    "avg_priority", "max_priority", "elapsed_minutes",
    "trace_hour", "day_of_trace", "is_peak_period",
]

def make_model(iterations):
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
        verbose=200,
    )

def score(actual, predicted):
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted)),
    }

def main():
    df = pd.read_csv(DATA).sort_values(
        ["timestamp_us", "machine_id"]
    ).reset_index(drop=True)

    timestamps = np.sort(df["timestamp_us"].unique())
    n = len(timestamps)
    train_end = int(n * 0.70)
    val_end = int(n * 0.85)

    train = df[df.timestamp_us.isin(timestamps[:train_end])]
    val = df[df.timestamp_us.isin(timestamps[train_end:val_end])]
    test = df[df.timestamp_us.isin(timestamps[val_end:])]

    results = {
        "experiment": "final log1p CPU and memory candidates",
        "split": "chronological 70/15/15",
        "test_used_for_selection": False,
        "targets": {},
    }

    for target, name in [
        ("actual_cpu", "cpu"),
        ("actual_memory", "memory"),
    ]:
        print(f"\n=== {name.upper()} ===")
        X_train, X_val = train[FEATURES], val[FEATURES]
        y_train, y_val = train[target], val[target]

        # Select the iteration count using validation data only.
        selector = make_model(1200)
        selector.fit(
            X_train, np.log1p(y_train),
            eval_set=(X_val, np.log1p(y_val)),
            early_stopping_rounds=100,
            verbose=200,
        )

        best = selector.get_best_iteration()
        iterations = max(1, best + 1) if best >= 0 else 1200

        # Refit on train + validation, then evaluate once on held-out test.
        trainval = pd.concat([train, val], ignore_index=True)
        final_model = make_model(iterations)
        final_model.fit(
            trainval[FEATURES],
            np.log1p(trainval[target]),
            verbose=200,
        )

        prediction = np.maximum(
            np.expm1(final_model.predict(test[FEATURES])), 0
        )
        baseline = np.full(len(test), trainval[target].mean())
        actual = test[target].to_numpy()

        final_path = MODEL_DIR / f"expected_resource_{name}_log.cbm"
        final_model.save_model(str(final_path))

        results["targets"][name] = {
            "target": target,
            "features": FEATURES,
            "best_validation_iteration": int(best),
            "final_iterations": int(iterations),
            "test_metrics": score(actual, prediction),
            "mean_baseline_test_metrics": score(actual, baseline),
            "model_path": str(final_path.relative_to(ROOT)),
            "test_rows": int(len(test)),
            "test_timestamps": int(test.timestamp_us.nunique()),
        }

        pd.DataFrame({
            "timestamp_us": test.timestamp_us.to_numpy(),
            "machine_id": test.machine_id.to_numpy(),
            "actual": actual,
            "predicted": prediction,
            "baseline_predicted": baseline,
        }).to_csv(
            META_DIR / f"{name}_log_test_predictions.csv",
            index=False,
        )

        print(json.dumps(results["targets"][name], indent=2))

    output = META_DIR / "final_log_target_test_metrics.json"
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved final experiment results: {output}")
    print("Original models and original prediction files were not overwritten.")

if __name__ == "__main__":
    main()
