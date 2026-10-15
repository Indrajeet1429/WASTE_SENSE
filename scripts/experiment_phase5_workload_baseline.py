
from pathlib import Path
import json

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/training/machine_resource_features_final_power_pdu.csv"
META = ROOT / "ml/artifacts/metadata"

TARGETS = {"cpu": "actual_cpu", "memory": "actual_memory"}
BIN_COUNTS = [5, 10, 20]


def metrics(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted)),
    }


def make_bins(reference, values, count):
    # Fit bin boundaries on reference data only.
    _, edges = pd.qcut(
        reference["active_tasks"],
        q=count,
        retbins=True,
        duplicates="drop",
    )
    edges = np.unique(edges.astype(float))
    if len(edges) < 2:
        return pd.Series(0, index=values.index, dtype=int)

    edges[0] = -np.inf
    edges[-1] = np.inf
    result = pd.cut(
        values["active_tasks"],
        bins=edges,
        labels=False,
        include_lowest=True,
    )
    return result.fillna(0).astype(int)


def fit_baseline(reference, target, count):
    frame = reference[["pdu", "active_tasks", target]].copy()
    frame["workload_bin"] = make_bins(
        reference, reference, count
    )

    # Fine-grained expectation for the same PDU and similar task count.
    grouped = frame.groupby(
        ["pdu", "workload_bin"], observed=True
    )[target].mean()

    # Fallbacks for bins not observed in training data.
    pdu_means = frame.groupby("pdu")[target].mean()
    global_mean = float(frame[target].mean())

    return grouped, pdu_means, global_mean


def predict_baseline(reference, query, target, count, fitted=None):
    if fitted is None:
        fitted = fit_baseline(reference, target, count)

    grouped, pdu_means, global_mean = fitted
    query_bins = make_bins(reference, query, count)

    keys = pd.MultiIndex.from_arrays(
        [query["pdu"].to_numpy(), query_bins.to_numpy()],
        names=["pdu", "workload_bin"],
    )
    predictions = grouped.reindex(keys).to_numpy(dtype=float)

    missing = ~np.isfinite(predictions)
    if missing.any():
        predictions[missing] = (
            query.loc[missing, "pdu"]
            .map(pdu_means)
            .fillna(global_mean)
            .to_numpy(dtype=float)[missing]
        )

    return np.maximum(predictions, 0)


def main():
    df = pd.read_csv(DATA)
    required = {
        "timestamp_us", "machine_id", "pdu", "active_tasks",
        "actual_cpu", "actual_memory",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing dataset columns: {missing}")

    if not np.isfinite(
        df[["active_tasks", "actual_cpu", "actual_memory"]]
        .to_numpy(dtype=float)
    ).all():
        raise ValueError("Non-finite values found")

    df = df.sort_values(
        ["timestamp_us", "machine_id"]
    ).reset_index(drop=True)
    df["pdu"] = df["pdu"].astype(str)

    timestamps = np.sort(df["timestamp_us"].unique())
    train_end = int(len(timestamps) * 0.70)
    val_end = int(len(timestamps) * 0.85)

    train = df[df["timestamp_us"].isin(set(timestamps[:train_end]))].copy()
    val = df[df["timestamp_us"].isin(set(timestamps[train_end:val_end]))].copy()
    trainval = pd.concat([train, val], ignore_index=True)
    test = df[df["timestamp_us"].isin(set(timestamps[val_end:]))].copy()

    results = {
        "experiment": "PDU + active-task-count grouped mean baseline",
        "split": "Chronological 70/15/15",
        "bin_counts_tested": BIN_COUNTS,
        "results": {},
    }

    for name, target in TARGETS.items():
        # Select bin count using validation only.
        validation_results = []
        for count in BIN_COUNTS:
            prediction = predict_baseline(train, val, target, count)
            validation_results.append({
                "bins": count,
                "mae": float(mean_absolute_error(val[target], prediction)),
            })

        selected = min(validation_results, key=lambda item: item["mae"])
        count = selected["bins"]

        # Refit grouped means on train + validation, then test once.
        fitted = fit_baseline(trainval, target, count)
        prediction = predict_baseline(
            trainval, test, target, count, fitted=fitted
        )

        original = pd.read_csv(META / f"{name}_test_predictions.csv")
        keys = ["timestamp_us", "machine_id"]
        if not set(keys + ["actual", "predicted"]).issubset(original.columns):
            raise ValueError(f"{name}: original prediction file lacks join columns")

        comparison = test[keys + [target]].merge(
            original[keys + ["actual", "predicted"]],
            on=keys,
            how="left",
            validate="one_to_one",
        )
        if comparison["predicted"].isna().any():
            raise ValueError(f"{name}: could not align original predictions")

        if not np.allclose(
            comparison[target].to_numpy(),
            comparison["actual"].to_numpy(),
        ):
            raise ValueError(f"{name}: test target alignment mismatch")

        results["results"][name] = {
            "validation_scores": validation_results,
            "selected_bins": count,
            "workload_baseline_test_metrics": metrics(
                test[target], prediction
            ),
            "original_model_test_metrics": metrics(
                comparison["actual"], comparison["predicted"]
            ),
            "trainval_global_mean_baseline_test_metrics": metrics(
                test[target],
                np.full(len(test), trainval[target].mean()),
            ),
        }

        print(f"\n{name.upper()}")
        print("Validation results:", validation_results)
        print("Selected bins:", count)
        print("Workload-aware baseline:",
              results["results"][name]["workload_baseline_test_metrics"])
        print("Original model:",
              results["results"][name]["original_model_test_metrics"])
        print("Global mean baseline:",
              results["results"][name]["trainval_global_mean_baseline_test_metrics"])

    output = META / "phase5_workload_baseline_experiment.json"
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults saved to: {output}")
    print("Production models were not modified.")


if __name__ == "__main__":
    main()
