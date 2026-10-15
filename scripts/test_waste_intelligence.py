from ml.pipeline.waste_detection import analyze_resource_waste
from ml.pipeline.waste_intelligence import (
    build_waste_fingerprint,
    detect_waste_persistence,
    analyze_root_cause,
)


def make_analysis(actual_cpu, expected_cpu, actual_memory, expected_memory):
    return analyze_resource_waste(
        actual_cpu=actual_cpu,
        expected_cpu=expected_cpu,
        cpu_capacity=1.0,
        actual_memory=actual_memory,
        expected_memory=expected_memory,
        memory_capacity=1.0,
    )


def test_fingerprint():
    normal = make_analysis(0.10, 0.10, 0.10, 0.10)
    result = build_waste_fingerprint(normal)
    assert result["fingerprint_type"] == "no_adjusted_excess"

    cpu = make_analysis(0.10, 0.02, 0.01, 0.01)
    result = build_waste_fingerprint(cpu)
    assert result["fingerprint_type"] == "cpu_dominant"

    memory = make_analysis(0.01, 0.01, 0.10, 0.02)
    result = build_waste_fingerprint(memory)
    assert result["fingerprint_type"] == "memory_dominant"
    print("PASS: Fingerprint classification")


def test_persistence():
    observations = [
        {"timestamp_us": 1_000_000, "waste_score": 10},
        {"timestamp_us": 2_000_000, "waste_score": 12},
        {"timestamp_us": 3_000_000, "waste_score": 11},
    ]
    result = detect_waste_persistence(
        observations,
        max_gap_seconds=2,
        score_threshold=5,
        minimum_observations=3,
    )
    assert result["persistence_detected"] is True
    assert result["latest_streak"]["observation_count"] == 3

    cleared = detect_waste_persistence(
        observations + [{"timestamp_us": 4_000_000, "waste_score": 0}],
        max_gap_seconds=2,
        score_threshold=5,
        minimum_observations=3,
    )
    assert cleared["persistence_detected"] is False
    print("PASS: Persistence and streak clearing")


def test_root_cause():
    analysis = make_analysis(0.10, 0.02, 0.01, 0.01)
    result = analyze_root_cause(
        analysis,
        workload_context={"active_tasks": 5},
    )
    assert result["status"] == "root_cause_hypotheses_generated"
    assert result["fingerprint_type"] == "cpu_dominant"
    assert result["root_cause_confirmed"] is False
    assert result["hypotheses"]
    print("PASS: Root-cause hypotheses remain unconfirmed")


def test_invalid_inputs():
    try:
        build_waste_fingerprint({})
    except (ValueError, KeyError, TypeError):
        pass
    else:
        raise AssertionError("Invalid fingerprint input was accepted")

    try:
        detect_waste_persistence(
            [{"timestamp_us": 1, "waste_score": 5},
             {"timestamp_us": 1, "waste_score": 6}],
            max_gap_seconds=2,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Duplicate timestamps were accepted")

    try:
        analyze_root_cause(
            make_analysis(0.10, 0.02, 0.01, 0.01),
            workload_context=[],
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid workload context was accepted")
    print("PASS: Invalid inputs rejected")


if __name__ == "__main__":
    test_fingerprint()
    test_persistence()
    test_root_cause()
    test_invalid_inputs()
    print("ALL WASTE INTELLIGENCE REGRESSION TESTS PASSED")
