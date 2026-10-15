
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

BASE_FEATURES = [
    "active_tasks", "cpu_capacity", "memory_capacity",
    "avg_priority", "max_priority", "elapsed_minutes",
    "trace_hour", "day_of_trace", "is_peak_period",
]
FEATURES = BASE_FEATURES + ["pdu"]
TARGETS = {"cpu": "actual_cpu", "memory": "actual_memory"}
SEED = 42


def metrics(actual, predicted):
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted)),
    }


def main():
    df = pd.read_csv(DATA)
    required = set(FEATURES + list(TARGETS.values()) + ["timestamp_us"])
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if df["pdu"].isna().any():
        raise ValueError("PDU contains missing values")

    df["pdu"] = df["pdu"].astype(str)
    timestamps = np.sort(df["timestamp_us"].unique())
    train_end = int(len(timestamps) * 0.70)
    val_end = int(len(timestamps) * 0.85)

    train_times = set(timestamps[:train_end])
    val_times = set(timestamps[train_end:val_end])
    test_times = set(timestamps[val_end:])

    train = df[df["timestamp_us"].isin(train_times)].copy()
    val = df[df["timestamp_us"].isin(val_times)].copy()
    test = df[df["timestamp_us"].isin(test_times)].copy()
    trainval = pd.concat([train, val], ignore_index=True)

    results = {
        "experiment": "Add categorical PDU feature to CPU/memory models",
        "split": "Chronological 70/15/15",
        "features": FEATURES,
        "results": {},
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    META_DIR.mkdir(parents=True, exist_ok=True)

    for name, target in TARGETS.items():
        print(f"\nTraining {name.upper()} candidate with PDU feature...")

        candidate = CatBoostRegressor(
            iterations=1200,
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

        candidate.fit(
            train[FEATURES],
            train[target],
            cat_features=["pdu"],
            eval_set=(val[FEATURES], val[target]),
            early_stopping_rounds=100,
            verbose=100,
        )

        best_iteration = candidate.get_best_iteration()
        iterations = max(50, best_iteration + 1) if best_iteration >= 0 else 1200

        final_model = CatBoostRegressor(
            iterations=iterations,
            depth=7,
            learning_rate=0.04,
            loss_function="RMSE",
            eval_metric="RMSE",
            task_type="GPU",
            devices="0",
            random_seed=SEED,
            allow_writing_files=False,
            verbose=False,
        )
        final_model.fit(
            trainval[FEATURES],
            trainval[target],
            cat_features=["pdu"],
            verbose=False,
        )

        actual = test[target].to_numpy(dtype=float)
        predicted = final_model.predict(test[FEATURES])
        baseline_value = float(trainval[target].mean())
        baseline = np.full(len(test), baseline_value)

        candidate_metrics = metrics(actual, predicted)
        baseline_metrics = metrics(actual, baseline)

        # Compare with the already evaluated original model on identical test rows.
        original_predictions = pd.read_csv(
            META_DIR / f"{name}_test_predictions.csv"
        )
        if len(original_predictions) != len(test):
            raise ValueError(
                f"{name}: original prediction count does not match test rows"
            )

        original_metrics = metrics(
            original_predictions["actual"],
            original_predictions["predicted"],
        )

        results["results"][name] = {
            "best_validation_iteration": int(best_iteration),
            "candidate_test_metrics": candidate_metrics,
            "corrected_trainval_mean_baseline": baseline_metrics,
            "original_model_test_metrics": original_metrics,
            "candidate_mae_improvement_vs_baseline_percent": float(
                100 * (baseline_metrics["mae"] - candidate_metrics["mae"])
                / baseline_metrics["mae"]
            ),
            "candidate_mae_improvement_vs_original_percent": float(
                100 * (
                    original_metrics["mae"] - candidate_metrics["mae"]
                ) / original_metrics["mae"]
            ),
            "candidate_model_path": (
                f"ml/artifacts/models/expected_resource_{name}_pdu_candidate.cbm"
            ),
        }

        final_model.save_model(
            str(MODEL_DIR / f"expected_resource_{name}_pdu_candidate.cbm")
        )

        print("Original model:", original_metrics)
        print("PDU candidate:", candidate_metrics)
        print("Corrected baseline:", baseline_metrics)

    output = META_DIR / "phase5_pdu_feature_experiment.json"
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nExperiment results saved to: {output}")


if __name__ == "__main__":
    main()
