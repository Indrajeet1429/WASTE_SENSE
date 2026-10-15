from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "ml" / "artifacts" / "metadata"

FILES = {
    "CPU": "cpu_test_predictions.csv",
    "Memory": "memory_test_predictions.csv",
    "Power": "power_test_predictions.csv",
}

# Diagnostic threshold only; not a calibrated anomaly threshold.
ABS_RESIDUAL_THRESHOLD = None


def main():
    for resource, filename in FILES.items():
        path = META / filename
        if not path.is_file():
            raise FileNotFoundError(f"Prediction artifact missing: {path}")

        df = pd.read_csv(path)
        required = {"actual", "predicted", "baseline_predicted"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"{filename} is missing columns: {sorted(missing)}")

        df = df.dropna(subset=list(required)).copy()
        values = df[["actual", "predicted", "baseline_predicted"]].to_numpy(
            dtype=float
        )
        if not np.isfinite(values).all():
            raise ValueError(f"{filename} contains non-finite prediction values.")
        if df.empty:
            raise ValueError(f"{filename} has no complete prediction rows.")

        df["residual"] = df["actual"] - df["predicted"]
        df["absolute_residual"] = df["residual"].abs()
        df["baseline_residual"] = df["actual"] - df["baseline_predicted"]

        print(f"\n{'=' * 68}")
        print(f"{resource} residual diagnostics")
        print(f"Rows evaluated: {len(df)}")
        print(f"Mean signed residual: {df['residual'].mean():.8f}")
        print(f"Residual standard deviation: {df['residual'].std(ddof=0):.8f}")
        print(f"Median absolute residual: {df['absolute_residual'].median():.8f}")
        print(f"95th percentile absolute residual: "
              f"{df['absolute_residual'].quantile(0.95):.8f}")
        print(f"Maximum absolute residual: {df['absolute_residual'].max():.8f}")
        print(f"Model MAE: {df['absolute_residual'].mean():.8f}")
        print(f"Baseline MAE: {df['baseline_residual'].abs().mean():.8f}")

        if ABS_RESIDUAL_THRESHOLD is not None:
            rate = (
                df["absolute_residual"] > ABS_RESIDUAL_THRESHOLD
            ).mean()
            print(f"Threshold exceedance rate: {rate:.4%}")
            print("Note: This is not a false-positive rate without ground-truth labels.")

        print("Interpretation: residual diagnostics only; no anomaly labels supplied.")


if __name__ == "__main__":
    main()
