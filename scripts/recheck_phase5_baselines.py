
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/training/machine_resource_features_final_power_pdu.csv"
META = ROOT / "ml/artifacts/metadata"

def report(name, actual, predicted, baseline):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    baseline = np.asarray(baseline, dtype=float)

    print(f"\n{name.upper()}")
    for label, values in [("Model", predicted), ("Corrected baseline", baseline)]:
        print(
            f"{label}: "
            f"MAE={mean_absolute_error(actual, values):.8f}, "
            f"RMSE={np.sqrt(mean_squared_error(actual, values)):.8f}, "
            f"R2={r2_score(actual, values):.8f}"
        )

def main():
    df = pd.read_csv(DATA)
    timestamps = np.sort(df["timestamp_us"].unique())
    cutoff = int(len(timestamps) * 0.85)
    trainval_times = set(timestamps[:cutoff])

    # CPU and memory: baseline mean from machine-level train + validation.
    trainval = df[df["timestamp_us"].isin(trainval_times)]

    for resource, target in [
        ("cpu", "actual_cpu"),
        ("memory", "actual_memory"),
    ]:
        pred_file = META / f"{resource}_test_predictions.csv"
        pred = pd.read_csv(pred_file)
        baseline_value = float(trainval[target].mean())
        baseline = np.full(len(pred), baseline_value)
        report(resource, pred["actual"], pred["predicted"], baseline)

    # Power: reproduce PDU-time aggregation and use a separate
    # train + validation mean for each PDU.
    power = df.groupby(["timestamp_us", "pdu"], as_index=False).agg(
        actual_power=("actual_power", "first"),
        power_values=("actual_power", "nunique"),
    )
    if (power["power_values"] != 1).any():
        raise ValueError("Inconsistent power values within a PDU-time group")

    power = power.sort_values(["timestamp_us", "pdu"]).reset_index(drop=True)
    power_times = np.sort(power["timestamp_us"].unique())
    power_cutoff = int(len(power_times) * 0.85)
    power_trainval = power[power["timestamp_us"].isin(set(power_times[:power_cutoff]))]

    pred = pd.read_csv(META / "power_test_predictions.csv")
    pdu_means = power_trainval.groupby("pdu")["actual_power"].mean()
    if "pdu" not in pred.columns:
        raise ValueError("Power predictions file is missing its PDU column")

    baseline = pred["pdu"].map(pdu_means)
    if baseline.isna().any():
        raise ValueError("A test PDU has no training-plus-validation baseline")

    report("power", pred["actual"], pred["predicted"], baseline)

if __name__ == "__main__":
    main()
