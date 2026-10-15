from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.pipeline.waste_detection import (
    calculate_excess,
    normalize_excess,
    calculate_uncertainty_adjusted_excess,
    calculate_waste_score,
    assign_severity,
    analyze_resource_waste,
)


def must_raise(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise AssertionError(f"Expected ValueError from {function.__name__}")


result = calculate_excess(0.08, 0.05)
assert abs(result["signed_excess"] - 0.03) < 1e-12
assert abs(result["positive_excess"] - 0.03) < 1e-12

result = calculate_excess(0.02, 0.05)
assert abs(result["signed_excess"] + 0.03) < 1e-12
assert result["positive_excess"] == 0.0

result = normalize_excess(0.08, 0.05, 0.5)
assert abs(result["normalized_positive_excess"] - 0.06) < 1e-12
must_raise(normalize_excess, 0.08, 0.05, 0)
must_raise(normalize_excess, 0.08, 0.05, float("inf"))

result = calculate_uncertainty_adjusted_excess(0.06, 0.05, 0.5, 0.02)
assert result["adjusted_positive_excess"] == 0.0

result = calculate_uncertainty_adjusted_excess(0.10, 0.05, 0.5, 0.02)
assert abs(result["adjusted_positive_excess"] - 0.03) < 1e-12
assert abs(result["normalized_adjusted_excess"] - 0.06) < 1e-12
must_raise(calculate_uncertainty_adjusted_excess, 0.1, 0.05, 0.5, -0.1)

result = calculate_waste_score(0.06, 0.02)
assert abs(result["score"] - 4.0) < 1e-12
assert result["score_capped"] is False

result = calculate_waste_score(1.5, 1.0)
assert result["score"] == 100.0
assert result["raw_score"] == 125.0
assert result["score_capped"] is True
must_raise(calculate_waste_score, -0.1, 0.0)

severity_cases = [
    (0, "none_detected"),
    (0.01, "low"),
    (5, "moderate"),
    (15, "high"),
    (30, "critical"),
    (100, "critical"),
]
for score, expected in severity_cases:
    result = assign_severity(score)
    assert result["severity"] == expected
    assert result["thresholds_status"] == "provisional"

must_raise(assign_severity, -1)
must_raise(assign_severity, 101)
must_raise(assign_severity, float("nan"))

normal = analyze_resource_waste(0.10, 0.10, 0.50, 0.05, 0.05, 0.25)
assert normal["waste_score"]["score"] == 0.0
assert normal["severity"] == "none_detected"

small = analyze_resource_waste(0.105, 0.10, 0.50, 0.052, 0.05, 0.25)
assert small["waste_score"]["score"] == 0.0

high = analyze_resource_waste(0.30, 0.10, 0.50, 0.15, 0.05, 0.25)
assert high["waste_score"]["score"] > 0
assert high["severity"] == "critical"
assert high["status"] == "heuristic_analysis_completed"
assert len(high["limitations"]) >= 4

must_raise(analyze_resource_waste, -0.1, 0.1, 0.5, 0.05, 0.05, 0.25)

print("PASS: Excess and normalization")
print("PASS: Uncertainty adjustment")
print("PASS: Waste score and capping")
print("PASS: Severity boundaries")
print("PASS: End-to-end scenarios and invalid inputs")
print("ALL WASTE DETECTION REGRESSION TESTS PASSED")
