
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.pipeline.inference import analyze_workload

workload = {
    "active_tasks": 2,
    "cpu_capacity": 1,
    "memory_capacity": 1,
    "avg_priority": 1,
    "max_priority": 1,
    "elapsed_minutes": 10,
    "trace_hour": 12,
    "day_of_trace": 1,
    "is_peak_period": 0,
    "actual_cpu": 0.01,
    "actual_memory": 0.02,
}

result = analyze_workload(workload)

for resource in ("cpu", "memory"):
    item = result["resources"][resource]

    assert np.isfinite(item["expected"]), f"{resource}: invalid prediction"
    assert item["expected"] >= 0, f"{resource}: negative prediction"
    assert item["actual"] is not None, f"{resource}: actual missing"
    assert np.isclose(
        item["excess"], item["actual"] - item["expected"]
    ), f"{resource}: incorrect excess"

print("PASS: valid workload predictions")
print("PASS: actual resource values included")
print("PASS: excess calculations verified")

# NaN must be rejected.
invalid = {**workload, "avg_priority": float("nan")}

try:
    analyze_workload(invalid)
except ValueError:
    print("PASS: non-finite input rejected")
else:
    raise AssertionError("NaN input was accepted")

print("\nAll inference tests passed.")
