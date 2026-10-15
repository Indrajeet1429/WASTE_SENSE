
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.pipeline.inference import analyze_workload
from ml.pipeline.power_inference import predict_expected_power

DATA = ROOT / (
    "data/processed/training/"
    "machine_resource_features_final_power_pdu.csv"
)

RESOURCE_FEATURES = [
    "active_tasks", "cpu_capacity", "memory_capacity",
    "avg_priority", "max_priority", "elapsed_minutes",
    "trace_hour", "day_of_trace", "is_peak_period",
]

POWER_PDUS = ("pdu10", "pdu6", "pdu7", "pdu8", "pdu9")


def check(condition, message):
    if not condition:
        raise AssertionError(message)
    print(f"PASS: {message}")


def main():
    # 1. Load and validate the real dataset.
    df = pd.read_csv(DATA)
    check(not df.empty, "Processed dataset loaded")

    required = set(
        RESOURCE_FEATURES
        + [
            "timestamp_us", "machine_id", "pdu",
            "actual_cpu", "actual_memory", "actual_power",
        ]
    )
    check(required.issubset(df.columns), "Required dataset columns exist")

    # 2. Test machine-level CPU and memory inference.
    row = df.iloc[0]
    workload = {name: row[name] for name in RESOURCE_FEATURES}
    workload["actual_cpu"] = float(row["actual_cpu"])
    workload["actual_memory"] = float(row["actual_memory"])

    result = analyze_workload(workload)

    check(result["status"] == "prediction_completed",
          "Machine-level inference completed")

    for resource in ("cpu", "memory"):
        item = result["resources"][resource]
        check(
            np.isfinite(item["expected"]) and item["expected"] >= 0,
            f"{resource.upper()} prediction is finite and non-negative",
        )
        check(
            np.isclose(
                item["excess"],
                item["actual"] - item["expected"],
            ),
            f"{resource.upper()} excess calculation is correct",
        )

    check(
        result["power"]["status"] == "not_predicted",
        "Machine-level interface does not misrepresent power prediction",
    )

    # 3. Recreate the training-time PDU-time aggregation.
    groups = df.groupby(
        ["timestamp_us", "pdu"], as_index=False
    ).agg(
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

    check(
        (groups["power_values"] == 1).all(),
        "Power labels are consistent within each PDU-time group",
    )

    # Use an actual row from the held-out chronological test period.
    timestamps = np.sort(df["timestamp_us"].unique())
    test_start = int(len(timestamps) * 0.85)
    test_timestamps = set(timestamps[test_start:])
    test_groups = groups[groups["timestamp_us"].isin(test_timestamps)]

    check(not test_groups.empty, "Held-out PDU-time data is available")

    power_row = test_groups.iloc[0]
    pdu = str(power_row["pdu"])
    check(pdu in POWER_PDUS, f"Recognized PDU: {pdu}")

    power_input = {
        name: power_row[name]
        for name in [
            "machine_count", "total_active_tasks",
            "total_cpu_capacity", "total_memory_capacity",
            "mean_avg_priority", "max_priority",
            "elapsed_minutes", "trace_hour",
            "day_of_trace", "is_peak_period",
        ]
    }
    power_input["pdu"] = pdu

    for name in POWER_PDUS:
        power_input[f"pdu_{name}"] = int(name == pdu)

    power_result = predict_expected_power(power_input)

    check(
        power_result["status"] == "prediction_completed",
        "PDU-time power inference completed",
    )
    check(
        power_result["prediction_level"] == "PDU-time",
        "Power prediction uses the correct aggregation level",
    )

    prediction = power_result["expected_power"]
    actual = float(power_row["actual_power"])

    check(
        np.isfinite(prediction) and prediction >= 0,
        "Power prediction is finite and non-negative",
    )

    print("\nHeld-out PDU-time integration example")
    print("PDU:", pdu)
    print("Actual power:", actual)
    print("Expected power:", prediction)
    print("Absolute error:", abs(actual - prediction))

    print(
        "\nPASS: Phase 5 inference integration checks completed. "
        "This test validates integration, not overall model accuracy."
    )


if __name__ == "__main__":
    main()
