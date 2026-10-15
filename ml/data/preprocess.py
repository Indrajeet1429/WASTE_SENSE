"""
WASTESENSE - Preprocessing Pipeline

Combines data loading, cleaning, and timestamp processing
to produce the final intermediate dataset.

The original raw dataset is never modified.
"""

from pathlib import Path

import pandas as pd

from ml.data.loader import load_google_instance_usage
from ml.data.cleaner import clean_usage_data
from ml.data.temporal import add_time_features


# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Output directory
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"

# Output file
OUTPUT_FILE = INTERIM_DIR / "google_cluster_usage_cleaned.csv"


def preprocess_data() -> pd.DataFrame:
    """
    Run the complete preprocessing pipeline.

    Returns
    -------
    pandas.DataFrame
        Final intermediate dataset.
    """

    # --------------------------------------------------
    # 1. Load data
    # --------------------------------------------------
    print("Step 1/4: Loading Google ClusterData...")

    data = load_google_instance_usage()

    print(f"Loaded rows: {len(data)}")

    # --------------------------------------------------
    # 2. Clean data
    # --------------------------------------------------
    print("\nStep 2/4: Cleaning data...")

    data = clean_usage_data(data)

    print(f"Rows after cleaning: {len(data)}")

    # --------------------------------------------------
    # 3. Add timestamp features
    # --------------------------------------------------
    print("\nStep 3/4: Processing timestamps...")

    data = add_time_features(data)

    print("Timestamp features added.")

    # --------------------------------------------------
    # 4. Save intermediate dataset
    # --------------------------------------------------
    print("\nStep 4/4: Saving intermediate dataset...")

    INTERIM_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    data.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"Saved to: {OUTPUT_FILE}")

    return data


if __name__ == "__main__":

    print("WASTESENSE PREPROCESSING PIPELINE")
    print("=" * 50)

    final_data = preprocess_data()

    print("\n" + "=" * 50)
    print("PREPROCESSING COMPLETE")
    print("=" * 50)

    print(f"Final rows: {len(final_data)}")
    print(f"Final columns: {len(final_data.columns)}")

    print("\nFinal columns:")
    for column in final_data.columns:
        print(f"- {column}")

    print("\nDataset shape:")
    print(final_data.shape)

    print("\nMissing values:")
    print(
        final_data.isnull().sum().sum()
    )

    print("\nDuplicate rows:")
    print(
        final_data.duplicated().sum()
    )

    print("\nOutput file:")
    print(OUTPUT_FILE)