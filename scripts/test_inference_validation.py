
from pathlib import Path
import sys

# Add the WASTESENSE project root to Python's import path.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.pipeline.inference import analyze_workload

base = {
    "active_tasks": 2,
    "cpu_capacity": 1,
    "memory_capacity": 1,
    "avg_priority": 1,
    "max_priority": 1,
    "elapsed_minutes": 10,
    "trace_hour": 12,
    "day_of_trace": 1,
    "is_peak_period": 0,
}

cases = [
    ("Missing feature", {k: v for k, v in base.items()
                         if k != "active_tasks"}),
    ("Zero CPU capacity", {**base, "cpu_capacity": 0}),
    ("Negative task count", {**base, "active_tasks": -1}),
]

failed = []

for name, data in cases:
    try:
        analyze_workload(data)
        print(f"FAIL: {name} was accepted")
        failed.append(name)
    except (ValueError, TypeError) as exc:
        print(f"PASS: {name} rejected: {exc}")

if failed:
    raise AssertionError(f"Invalid cases accepted: {failed}")

print("\nAll invalid-input tests passed.")
