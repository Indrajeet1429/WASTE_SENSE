
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "ml/artifacts/metadata/phase5_model_selection_report.json"
EXPERIMENT = ROOT / "ml/artifacts/metadata/phase5_pdu_feature_experiment.json"

with REPORT.open(encoding="utf-8") as f:
    report = json.load(f)

with EXPERIMENT.open(encoding="utf-8") as f:
    experiment = json.load(f)

report["pdu_feature_experiment"] = {
    "results_file": str(EXPERIMENT.relative_to(ROOT)),
    "cpu_decision": (
        "Rejected for production selection: MAE improvement is tiny, "
        "while RMSE and R2 worsen."
    ),
    "memory_decision": (
        "Rejected for production selection: improvements across metrics "
        "are marginal and do not establish meaningful predictive gain."
    ),
    "production_models_changed": False,
    "results": experiment["results"],
}

report["completion_status"]["phase5_complete"] = False
report["completion_status"]["phase6_authorized"] = False

with REPORT.open("w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
    f.write("\n")

print("PASS: PDU-feature experiment documented.")
print("PASS: Existing production models remain unchanged.")
print("PASS: Phase 6 remains unauthorized.")
