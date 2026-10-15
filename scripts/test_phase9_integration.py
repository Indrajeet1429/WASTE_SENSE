from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.pipeline.waste_detection import analyze_resource_waste
from ml.pipeline.waste_intelligence import build_waste_fingerprint, analyze_root_cause
from ml.pipeline.recommendations import (
    generate_recommendations,
    generate_recommendations_from_analysis,
)


def check(condition, message):
    if not condition:
        raise AssertionError(message)
    print(f"PASS: {message}")


def main():
    workload = {
        "actual_cpu": 0.8,
        "expected_cpu": 0.5,
        "cpu_capacity": 1.0,
        "actual_memory": 0.7,
        "expected_memory": 0.4,
        "memory_capacity": 1.0,
    }

    waste = analyze_resource_waste(
        workload["actual_cpu"],
        workload["expected_cpu"],
        workload["cpu_capacity"],
        workload["actual_memory"],
        workload["expected_memory"],
        workload["memory_capacity"],
    )
    check(waste["status"] == "heuristic_analysis_completed",
          "Phase 6 waste analysis completed")

    fingerprint = build_waste_fingerprint(waste)
    root_cause = analyze_root_cause(waste)
    check(fingerprint["status"] == "fingerprint_generated",
          "Phase 7 waste fingerprint generated")
    check(root_cause["root_cause_confirmed"] is False,
          "Root-cause analysis remains unconfirmed")

    result = generate_recommendations_from_analysis(
        {
            "actual_cpu": workload["actual_cpu"],
            "expected_cpu": workload["expected_cpu"],
            "actual_memory": workload["actual_memory"],
            "expected_memory": workload["expected_memory"],
        },
        waste,
        persistence_analysis={
            "status": "persistence_analysis_completed",
            "persistence_detected": True,
        },
        root_cause_analysis=root_cause,
    )

    check(result["status"] == "recommendations_generated",
          "Phase 9 integrated recommendations generated")
    check(result["integration"]["status"] == "phase6_phase7_integration_completed",
          "Integration status reported")
    check(result["integration"]["root_cause_confirmed"] is False,
          "Integration does not claim confirmed root cause")
    check(
        all(item["priority"] == "medium" for item in result["recommendations"]),
        "Persistent signals with a normalized score below 0.7 receive medium priority",
    )
    check(
        all(item["requires_human_review"] for item in result["recommendations"]),
        "Integrated recommendations require human review",
    )

    # Verify the 0–100 waste score is converted to the 0–1 recommendation scale.
    score_100 = waste["waste_score"]["score"]
    expected_normalized = score_100 / 100.0
    direct = generate_recommendations({
        "actual_cpu": workload["actual_cpu"],
        "expected_cpu": workload["expected_cpu"],
        "actual_memory": workload["actual_memory"],
        "expected_memory": workload["expected_memory"],
        "waste_score": expected_normalized,
        "persistence_detected": True,
    })
    check(
        len(direct["recommendations"]) == len(result["recommendations"]),
        "Integrated and direct recommendation counts agree",
    )

    print("\nALL PHASE 9 INTEGRATION TESTS PASSED")


if __name__ == "__main__":
    main()

