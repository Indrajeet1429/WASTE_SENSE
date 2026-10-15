
from pathlib import Path
from catboost import CatBoostRegressor
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "ml" / "artifacts" / "models"

models = {
    "expected_resource_cpu.cbm": 9,
    "expected_resource_memory.cbm": 9,
    "expected_resource_power.cbm": 15,
    "expected_resource_cpu_log.cbm": 9,
    "expected_resource_memory_log.cbm": 9,
}

failed = []

for filename, expected_count in models.items():
    path = MODEL_DIR / filename

    try:
        if not path.is_file():
            raise FileNotFoundError(f"Missing model: {path}")

        model = CatBoostRegressor()
        model.load_model(str(path))

        feature_names = model.feature_names_
        if len(feature_names) != expected_count:
            raise AssertionError(
                f"Expected {expected_count} features, "
                f"found {len(feature_names)}"
            )

        print(
            f"PASS: {filename} loaded; "
            f"{len(feature_names)} features"
        )

    except Exception as exc:
        failed.append(filename)
        print(f"FAIL: {filename}: {exc}")

if failed:
    raise AssertionError(f"Artifact validation failed: {failed}")

print("\nAll five model artifacts passed loading and feature-count checks.")
