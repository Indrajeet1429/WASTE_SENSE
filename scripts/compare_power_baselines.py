import pandas as pd
from pathlib import Path
from sklearn.metrics import mean_absolute_error

data_path = Path("data/processed/training/machine_resource_features_final_power_pdu.csv")
pred_path = Path("ml/artifacts/metadata/power_test_predictions.csv")

df = pd.read_csv(data_path)
df = df.sort_values(["timestamp_us", "pdu"])

times = sorted(df["timestamp_us"].unique())
train_times = set(times[:int(len(times) * 0.70)])
test_times = set(times[int(len(times) * 0.85):])

train = df[df["timestamp_us"].isin(train_times)]
test = df[df["timestamp_us"].isin(test_times)]

train_power = train.groupby("pdu")["actual_power"].mean()
pred = pd.read_csv(pred_path)

pred["pdu_mean_prediction"] = pred["pdu"].map(train_power)

print("POWER MODEL VS TRAINING-ONLY PDU-MEAN BASELINE")
print("Model MAE:", round(mean_absolute_error(pred["actual"], pred["predicted"]), 8))
print("PDU-mean baseline MAE:", round(mean_absolute_error(pred["actual"], pred["pdu_mean_prediction"]), 8))
print("\nPER-PDU COMPARISON")

for pdu, group in pred.groupby("pdu"):
    print(
        pdu,
        "| model MAE:", round(mean_absolute_error(group["actual"], group["predicted"]), 8),
        "| PDU baseline MAE:", round(mean_absolute_error(group["actual"], group["pdu_mean_prediction"]), 8),
    )
