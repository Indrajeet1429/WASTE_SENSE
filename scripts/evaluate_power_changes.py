import pandas as pd
from pathlib import Path
from sklearn.metrics import mean_absolute_error

path = Path("ml/artifacts/metadata/power_test_predictions.csv")
df = pd.read_csv(path).sort_values(["pdu", "timestamp_us"])

df["actual_change"] = df.groupby("pdu")["actual"].diff()
df["predicted_change"] = df.groupby("pdu")["predicted"].diff()
df = df.dropna(subset=["actual_change", "predicted_change"])

print("POWER CHANGE TRACKING")
print("Change observations:", len(df))
print("Actual-change MAE baseline (predict no change):",
      round(mean_absolute_error(df["actual_change"], 0 * df["actual_change"]), 8))
print("Model change MAE:",
      round(mean_absolute_error(df["actual_change"], df["predicted_change"]), 8))

print("\nPER-PDU CHANGE MAE")
for pdu, group in df.groupby("pdu"):
    baseline_mae = mean_absolute_error(group["actual_change"], 0 * group["actual_change"])
    model_mae = mean_absolute_error(group["actual_change"], group["predicted_change"])
    print(pdu, "| model:", round(model_mae, 8), "| no-change baseline:", round(baseline_mae, 8))
