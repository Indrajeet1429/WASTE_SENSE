import pandas as pd
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

path = Path("ml/artifacts/metadata/power_test_predictions.csv")
df = pd.read_csv(path)

print("TEST ROWS:", len(df))
print("UNIQUE TIMESTAMPS:", df["timestamp_us"].nunique())
print("\nMETRICS BY PDU:")

for pdu, group in df.groupby("pdu"):
    actual = group["actual"]
    predicted = group["predicted"]
    baseline = group["baseline_predicted"]

    print(f"\n{pdu} | rows={len(group)}")
    print("Actual mean:", round(actual.mean(), 6))
    print("Predicted mean:", round(predicted.mean(), 6))
    print("Model MAE:", round(mean_absolute_error(actual, predicted), 6))
    print("Baseline MAE:", round(mean_absolute_error(actual, baseline), 6))
    if len(group) >= 2:
        print("Model R2:", round(r2_score(actual, predicted), 6))
