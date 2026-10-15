import unittest

from ml.pipeline.inference import analyze_workload


class TestInferenceIntegration(unittest.TestCase):
    def setUp(self):
        self.features = {
            "active_tasks": 3,
            "cpu_capacity": 1.0,
            "memory_capacity": 1.0,
            "avg_priority": 1.0,
            "max_priority": 2.0,
            "elapsed_minutes": 10.0,
            "trace_hour": 12,
            "day_of_trace": 1,
            "is_peak_period": 0,
        }

    def test_prediction_without_actual_measurements(self):
        result = analyze_workload(self.features)
        self.assertEqual(result["status"], "prediction_completed")
        self.assertIsNone(result["resources"]["cpu"]["actual"])
        self.assertEqual(result["waste_analysis"]["status"], "not_available")
        self.assertEqual(result["power"]["status"], "not_predicted")

    def test_end_to_end_analysis_with_actual_measurements(self):
        inputs = {
            **self.features,
            "actual_cpu": 0.8,
            "actual_memory": 0.7,
        }
        result = analyze_workload(inputs)

        self.assertEqual(result["status"], "prediction_completed")
        self.assertEqual(
            result["waste_analysis"]["status"],
            "heuristic_analysis_completed",
        )
        self.assertIn("score", result["waste_analysis"]["waste_score"])
        self.assertEqual(
            result["root_cause_analysis"]["status"],
            "root_cause_hypotheses_generated",
        )
        self.assertEqual(
            result["recommendations"]["integration"]["status"],
            "phase6_phase7_integration_completed",
        )
        self.assertEqual(result["power"]["status"], "not_predicted")
        self.assertIn("status", result["savings_estimate"])


    def test_optional_waste_replay(self):
        inputs = {
            **self.features,
            "actual_cpu": 0.8,
            "actual_memory": 0.7,
            "replay_observations": [
                {
                    "machine_id": "M-test",
                    "timestamp_us": 1000000,
                    "actual_cpu": 0.8,
                    "expected_cpu": 0.5,
                    "actual_memory": 0.7,
                    "expected_memory": 0.4,
                }
            ],
            "optimization_fraction": 0.5,
        }
        result = analyze_workload(inputs)

        self.assertEqual(result["replay"]["status"], "waste_replay_completed")
        self.assertEqual(result["replay"]["observation_count"], 1)
        self.assertAlmostEqual(
            result["replay"]["totals"]["hypothetical_cpu_reduction"], 0.15
        )
        self.assertIsNone(result["replay"]["realized_savings"])


    def test_optional_pdu_time_power_inference(self):
        from ml.pipeline.inference import POWER_FEATURES

        power_input = {
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
        result = analyze_workload({
            **self.features,
            "power_input": power_input,
        })

        self.assertEqual(result["power"]["status"], "prediction_completed")
        self.assertEqual(result["power"]["prediction_level"], "PDU-time")
        self.assertTrue(result["power"]["expected_power"] >= 0)
        self.assertTrue(len(POWER_FEATURES) == 15)


if __name__ == "__main__":
    unittest.main()
