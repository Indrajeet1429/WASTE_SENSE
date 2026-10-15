
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.pipeline.power_inference import predict_expected_power

workload = {
    "pdu": "pdu10",
    "machine_count": 100,
    "total_active_tasks": 200,
    "total_cpu_capacity": 100,
    "total_memory_capacity": 100,
    "mean_avg_priority": 1,
    "max_priority": 1,
    "elapsed_minutes": 10,
    "trace_hour": 12,
    "day_of_trace": 1,
    "is_peak_period": 0,
    "pdu_pdu10": 1,
    "pdu_pdu6": 0,
    "pdu_pdu7": 0,
    "pdu_pdu8": 0,
    "pdu_pdu9": 0,
}

result = predict_expected_power(workload)
print(result)

assert np.isfinite(result["expected_power"])
assert result["expected_power"] >= 0
assert result["prediction_level"] == "PDU-time"

print("PASS: PDU-time power inference")
