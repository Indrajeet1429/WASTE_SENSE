
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.pipeline.power_inference import predict_expected_power

DATA = ROOT / (
    "data/processed/training/"
    "machine_resource_features_final_power_pdu.csv"
)

df = pd.read_csv(DATA)

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

assert (group["power_values"] == 1).all()
row = group.iloc[0]
pdu = str(row["pdu"])

workload = {
    "pdu": pdu,
    "machine_count": int(row["machine_count"]),
    "total_active_tasks": float(row["total_active_tasks"]),
    "total_cpu_capacity": float(row["total_cpu_capacity"]),
    "total_memory_capacity": float(row["total_memory_capacity"]),
    "mean_avg_priority": float(row["mean_avg_priority"]),
    "max_priority": float(row["max_priority"]),
    "elapsed_minutes": float(row["elapsed_minutes"]),
    "trace_hour": float(row["trace_hour"]),
    "day_of_trace": float(row["day_of_trace"]),
    "is_peak_period": float(row["is_peak_period"]),
}

for name in ("pdu10", "pdu6", "pdu7", "pdu8", "pdu9"):
    workload[f"pdu_{name}"] = int(pdu == name)

result = predict_expected_power(workload)
prediction = result["expected_power"]
actual = float(row["actual_power"])

print("PDU:", pdu)
print("Actual power:", actual)
print("Expected power:", prediction)
print("Absolute error:", abs(actual - prediction))

assert np.isfinite(prediction)
assert prediction >= 0
print("PASS: real-data PDU-time inference")
