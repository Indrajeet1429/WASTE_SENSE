from pathlib import Path
import json
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/training/machine_resource_features_final_power_pdu.csv"
OUT = ROOT / "ml/artifacts/metadata/power_rolling_validation.json"
SEED = 42

def make_model():
    return CatBoostRegressor(
        iterations=251,
        depth=7,
        learning_rate=0.04,
        loss_function="RMSE",
        task_type="GPU",
        devices="0",
        random_seed=SEED,
        allow_writing_files=False,
        verbose=False,
    )

def score(actual, predicted):
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted)) if len(actual) > 1 else None,
    }

def main():
    df = pd.read_csv(DATA).sort_values(["timestamp_us", "machine_id"])
    group = df.groupby(["timestamp_us", "pdu"], as_index=False).agg(
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

    if (group["power_values"] != 1).any():
        raise ValueError("Inconsistent power labels within timestamp/PDU groups")

    pdu_values = sorted(group["pdu"].unique())
    for pdu in pdu_values:
        group[f"pdu_{pdu}"] = (group["pdu"] == pdu).astype(int)

    features = [
        "machine_count", "total_active_tasks", "total_cpu_capacity",
        "total_memory_capacity", "mean_avg_priority", "max_priority",
        "elapsed_minutes", "trace_hour", "day_of_trace", "is_peak_period",
    ] + [f"pdu_{pdu}" for pdu in pdu_values]

    times = np.sort(group["timestamp_us"].unique())
    # Expanding-window evaluation: train only on earlier timestamps.
    # Use 60% initial history, then four non-overlapping future blocks.
    first_cut = int(len(times) * 0.60)
    remaining = times[first_cut:]
    blocks = [b for b in np.array_split(remaining, 4) if len(b) > 0]

    fold_results = []
    all_actual, all_pred, all_pdu_baseline = [], [], []

    for fold_number, block in enumerate(blocks, start=1):
        if len(block) == 0:
            continue

        train_times = times[times < block[0]]
        train = group[group["timestamp_us"].isin(train_times)]
        valid = group[group["timestamp_us"].isin(block)]

        if len(train_times) < 20 or valid.empty:
            print(f"Skipping fold {fold_number}: insufficient history or validation data")
            continue

        model = make_model()
        model.fit(train[features], train["actual_power"])

        pred = model.predict(valid[features])
        # Training-only PDU mean baseline
        pdu_means = train.groupby("pdu")["actual_power"].mean()
        pdu_baseline = valid["pdu"].map(pdu_means).to_numpy()
        # No-change baseline: previous observed power for the same PDU
        history = group[group["timestamp_us"] < block[0]]
        previous = history.sort_values("timestamp_us").groupby("pdu").tail(1)
        previous_power = previous.set_index("pdu")["actual_power"]
        no_change = valid["pdu"].map(previous_power).to_numpy()

        actual = valid["actual_power"].to_numpy()
        fold_results.append({
            "fold": fold_number,
            "train_timestamps": int(len(train_times)),
            "validation_timestamps": int(len(block)),
            "validation_groups": int(len(valid)),
            "model": score(actual, pred),
            "pdu_mean_baseline": score(actual, pdu_baseline),
            "no_change_baseline": score(actual, no_change),
        })

        all_actual.extend(actual)
        all_pred.extend(pred)
        all_pdu_baseline.extend(pdu_baseline)
        print(f"Fold {fold_number}: groups={len(valid)}, model MAE={mean_absolute_error(actual, pred):.6f}, PDU baseline MAE={mean_absolute_error(actual, pdu_baseline):.6f}")

    if not fold_results:
        raise RuntimeError("No valid rolling-origin folds were evaluated")

    report = {
        "method": "expanding-window chronological validation",
        "folds": fold_results,
        "pooled_model_metrics": score(np.array(all_actual), np.array(all_pred)),
        "pooled_pdu_mean_baseline_metrics": score(np.array(all_actual), np.array(all_pdu_baseline)),
        "warning": "Small time-series dataset; use results as preliminary evidence.",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nPOOLED RESULTS")
    print(json.dumps({
        "model": report["pooled_model_metrics"],
        "pdu_mean_baseline": report["pooled_pdu_mean_baseline_metrics"],
    }, indent=2))
    print(f"\nSaved report: {OUT}")

if __name__ == "__main__":
    main()
