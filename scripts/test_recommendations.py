from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.pipeline.recommendations import generate_recommendations


def check(condition, message):
    if not condition:
        raise AssertionError(message)
    print(f"PASS: {message}")


def must_raise(function, expected_exception=ValueError):
    try:
        function()
    except expected_exception:
        return
    raise AssertionError(f"Expected {expected_exception.__name__}")


def main():
    # Positive excess produces recommendations.
    result = generate_recommendations({
        "actual_cpu": 0.8,
        "expected_cpu": 0.5,
        "actual_memory": 0.7,
        "expected_memory": 0.4,
        "waste_score": 0.8,
        "persistence_detected": True,
        "root_cause_hypotheses": ["Possible over-allocation"],
    })

    check(result["status"] == "recommendations_generated",
          "Recommendation generation completes")
    check(result["recommendation_count"] == 2,
          "CPU and memory recommendations are generated")
    check(all(item["priority"] == "high"
              for item in result["recommendations"]),
          "Persistent high-score waste receives high heuristic priority")
    check(all(item["requires_human_review"]
              for item in result["recommendations"]),
          "Recommendations require human review")
    check(all(item["estimated_savings"] is None
              for item in result["recommendations"]),
          "Recommendations do not claim estimated savings")
    check(all(item["root_cause_hypotheses"] == ["Possible over-allocation"]
              for item in result["recommendations"]),
          "Root-cause hypotheses are passed through without confirmation")

    # No positive excess should not produce actions.
    no_excess = generate_recommendations({
        "actual_cpu": 0.2,
        "expected_cpu": 0.3,
        "actual_memory": 0.4,
        "expected_memory": 0.4,
    })
    check(no_excess["recommendation_count"] == 0,
          "No positive excess produces no recommendations")

    # Priority order must be deterministic.
    ordered = generate_recommendations({
        "actual_cpu": 0.9,
        "expected_cpu": 0.5,
        "actual_memory": 0.7,
        "expected_memory": 0.4,
        "waste_score": 0.8,
        "persistence_detected": True,
    })
    check(
        [item["resource"] for item in ordered["recommendations"]]
        == ["cpu", "memory"],
        "Equal-priority recommendations use deterministic ordering",
    )

    # Reject invalid input and invalid optional values.
    must_raise(lambda: generate_recommendations([]), TypeError)
    must_raise(lambda: generate_recommendations({"actual_cpu": 0.1}))
    must_raise(lambda: generate_recommendations({
        "actual_cpu": float("nan"),
        "expected_cpu": 0.1,
        "actual_memory": 0.1,
        "expected_memory": 0.1,
    }))
    must_raise(lambda: generate_recommendations({
        "actual_cpu": 0.1,
        "expected_cpu": 0.1,
        "actual_memory": 0.1,
        "expected_memory": 0.1,
        "waste_score": 1.1,
    }))
    must_raise(lambda: generate_recommendations({
        "actual_cpu": 0.1,
        "expected_cpu": 0.1,
        "actual_memory": 0.1,
        "expected_memory": 0.1,
        "persistence_detected": "yes",
    }))
    check(True, "Invalid inputs and optional values are rejected")

    print("\nALL RECOMMENDATION TESTS PASSED")


if __name__ == "__main__":
    main()
