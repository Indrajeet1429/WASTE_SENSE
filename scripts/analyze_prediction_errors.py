import pandas as pd
from pathlib import Path
from sklearn.metrics import mean_absolute_error

folder = Path("ml/artifacts/metadata")

for filename in ["cpu_test_predictions.csv", "memory_test_predictions.csv"]:
    path = folder / filename
    df = pd.read_csv(path)

    df = df.dropna(subset=["actual", "predicted", "baseline_predicted"])
    df["model_error"] = (df["actual"] - df["predicted"]).abs()
    df["baseline_error"] = (df["actual"] - df["baseline_predicted"]).abs()

    print("\n" + "=" * 75)
    print("FILE:", filename)
    print("OVERALL MODEL MAE:", round(mean_absolute_error(df["actual"], df["predicted"]), 8))
    print("OVERALL BASELINE MAE:", round(mean_absolute_error(df["actual"], df["baseline_predicted"]), 8))

    df["usage_group"] = pd.qcut(df["actual"], q=5, duplicates="drop")

    print("\nERROR BY ACTUAL RESOURCE-USAGE GROUP:")
    summary = df.groupby("usage_group", observed=True).agg(
        rows=("actual", "size"),
        mean_actual=("actual", "mean"),
        mean_predicted=("predicted", "mean"),
        model_MAE=("model_error", "mean"),
        baseline_MAE=("baseline_error", "mean")
    )

    print(summary.round(8).to_string())
