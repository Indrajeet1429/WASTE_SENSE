from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.data.validator import validate_usage_data

def make_data():
    return pd.DataFrame({
        "start_time": [0, 0],
        "end_time": [300_000_000, 300_000_000],
        "collection_id": [1, 2],
        "instance_index": [0, 1],
        "machine_id": [1, 2],
        "cpu_usage": [0.1, 0.2],
        "memory_usage": [0.1, 0.2],
        "alloc_collection_id": [0, 0],
        "duration_us": [300_000_000, 300_000_000],
    })

df = make_data()
result = validate_usage_data(df)
assert result["cpu_infinite"] == 0
assert result["cpu_infinite_values"] == 0
assert result["memory_infinite_values"] == 0
print("PASS: finite values")

df = make_data()
df.loc[0, "cpu_usage"] = float("inf")
df.loc[1, "cpu_usage"] = float("-inf")
df.loc[0, "memory_usage"] = float("inf")
result = validate_usage_data(df)
assert result["cpu_infinite_values"] == 2, result
assert result["memory_infinite_values"] == 1, result
assert result["validation_errors"] >= 3, result
print("PASS: positive and negative infinity")

df = make_data()
df.loc[0, "cpu_usage"] = float("nan")
df.loc[1, "memory_usage"] = float("nan")
result = validate_usage_data(df)
assert result["missing_values"] == 2, result
assert result["cpu_infinite_values"] == 0, result
assert result["memory_infinite_values"] == 0, result
print("PASS: missing values counted separately")

print("All validator regression tests passed.")
