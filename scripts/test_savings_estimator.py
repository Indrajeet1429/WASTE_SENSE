from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.pipeline.savings_estimator import (
    estimate_resource_savings,
    estimate_savings,
)


def must_raise(function, *args):
    try:
        function(*args)
    except (ValueError, TypeError):
        return
    raise AssertionError(f"Expected validation error from {function.__name__}")


result = estimate_resource_savings(0.08, 0.05, "cpu")
assert abs(result["signed_excess"] - 0.03) < 1e-12
assert abs(result["potential_excess"] - 0.03) < 1e-12
assert result["realized_savings"] is None

result = estimate_resource_savings(0.02, 0.05, "memory")
assert abs(result["signed_excess"] + 0.03) < 1e-12
assert result["potential_excess"] == 0.0

for invalid in (-1, float("nan"), float("inf"), float("-inf"), None, True):
    must_raise(estimate_resource_savings, invalid, 0.05, "cpu")

must_raise(estimate_resource_savings, 0.1, -0.1, "cpu")
must_raise(estimate_resource_savings, 0.1, 0.05, "")

result = estimate_savings({
    "actual_cpu": 0.08,
    "expected_cpu": 0.05,
    "actual_memory": 0.04,
    "expected_memory": 0.03,
})
assert result["status"] == "potential_savings_estimated"
assert abs(result["cpu"]["potential_excess"] - 0.03) < 1e-12
assert abs(result["memory"]["potential_excess"] - 0.01) < 1e-12
assert result["power"]["status"] == "not_estimated"
assert result["cpu"]["realized_savings"] is None

must_raise(estimate_savings, {})
must_raise(estimate_savings, None)

print("PASS: Positive and negative excess calculations")
print("PASS: Invalid and non-finite input validation")
print("PASS: CPU and memory estimate output contract")
print("PASS: Power is not falsely estimated")
print("ALL SAVINGS ESTIMATOR TESTS PASSED")
