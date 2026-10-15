
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "ml/artifacts/metadata/phase5_model_selection_report.json"

with REPORT.open("r", encoding="utf-8") as f:
    report = json.load(f)

cpu = report["model_selection"]["cpu"]
cpu["baseline_test_mae"] = 0.0080330539
cpu["baseline_test_rmse"] = 0.01552105
cpu["baseline_test_r2"] = -0.00936038
cpu["decision"] = (
    "Provisional candidate only. Corrected baseline comparison shows "
    "about 0.21% lower MAE and better RMSE/R2, but absolute predictive "
    "performance remains weak."
)

memory = report["model_selection"]["memory"]
memory["baseline_test_mae"] = 0.0038242189
memory["baseline_test_rmse"] = 0.00803195
memory["baseline_test_r2"] = -0.00632300
memory["decision"] = (
    "Provisional candidate only. MAE is about 0.19% worse than the "
    "corrected baseline, although RMSE and R2 improve slightly; "
    "meaningful predictive improvement is not established."
)

power = report["model_selection"]["power"]
power["baseline_test_mae"] = 0.03203393
power["baseline_test_rmse"] = 0.03307821
power["baseline_test_r2"] = -1.62069328
power["decision"] = (
    "Retain as a candidate for absolute PDU-time power estimation. "
    "It substantially beats the corrected PDU-specific mean baseline, "
    "but the test set is small and temporal change tracking is not validated."
)

report["completion_status"]["phase5_complete"] = False
report["completion_status"]["phase6_authorized"] = False
report["completion_status"]["remaining"] = [
    "Review and approve the documented model-selection decisions.",
    "Run final regression and repository checks.",
    "Commit and push the approved Phase 5 report and validation files."
]

with REPORT.open("w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
    f.write("\n")

# Verify that the saved report remains valid JSON.
with REPORT.open("r", encoding="utf-8") as f:
    verified = json.load(f)

assert verified["completion_status"]["phase5_complete"] is False
assert verified["completion_status"]["phase6_authorized"] is False

print("PASS: Corrected baseline metrics saved.")
print("PASS: Model-selection decisions updated.")
print("PASS: Phase 5 remains open; Phase 6 remains unauthorized.")
