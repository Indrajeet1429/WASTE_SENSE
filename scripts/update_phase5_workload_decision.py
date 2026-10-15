
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "ml/artifacts/metadata/phase5_model_selection_report.json"
EXPERIMENT = ROOT / "ml/artifacts/metadata/phase5_workload_baseline_experiment.json"

with REPORT.open(encoding="utf-8") as f:
    report = json.load(f)

with EXPERIMENT.open(encoding="utf-8") as f:
    experiment = json.load(f)

report["workload_baseline_experiment"] = {
    "results_file": str(EXPERIMENT.relative_to(ROOT)),
    "decision": (
        "Workload-aware PDU/task-count grouped-mean baseline did not "
        "meaningfully improve overall CPU or memory prediction. "
        "Existing models remain provisional candidates."
    ),
    "production_models_changed": False,
    "results": experiment["results"],
}

report["completion_status"]["phase5_complete"] = False
report["completion_status"]["phase6_authorized"] = False
report["completion_status"]["remaining"] = [
    "Review and approve the documented provisional model-selection policy.",
    "Confirm final regression tests and repository state.",
    "Finalize Phase 5 acceptance documentation with explicit CPU/memory limitations.",
]

with REPORT.open("w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
    f.write("\n")

with REPORT.open(encoding="utf-8") as f:
    verified = json.load(f)

assert verified["completion_status"]["phase5_complete"] is False
assert verified["completion_status"]["phase6_authorized"] is False

print("PASS: Workload-baseline experiment documented.")
print("PASS: Production models remain unchanged.")
print("PASS: Phase 5 remains open pending final acceptance.")
print("PASS: Phase 6 remains unauthorized.")
