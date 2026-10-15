import pandas as pd
from pathlib import Path

folder = Path("ml/artifacts/metadata")
files = ["cpu_test_predictions.csv", "memory_test_predictions.csv"]

for filename in files:
    path = folder / filename
    print(f"\nFILE: {filename}")

    if not path.exists():
        print("ERROR: File not found:", path)
        continue

    df = pd.read_csv(path)
    print("COLUMNS:", df.columns.tolist())
    print("\nFIRST 3 ROWS:")
    print(df.head(3).to_string(index=False))
    print("ROWS:", len(df))
