"""
WASTESENSE - Google ClusterData Loader

Loads the Google ClusterData 2019 instance usage sample
and applies the official filtering criteria.
"""

from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "google_clusterdata"
    / "google_cluster_instance_usage_sample.csv"
)


def load_google_instance_usage() -> pd.DataFrame:
    """
    Load and filter Google ClusterData 2019 instance usage data.

    Filtering:
    1. Keep top-level instances only:
       alloc_collection_id == 0

    2. Keep usage intervals of at least 5 minutes.

    Returns
    -------
    pandas.DataFrame
        Cleaned usage dataframe.
    """

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    required_columns = [
        "start_time",
        "end_time",
        "collection_id",
        "instance_index",
        "machine_id",
        "cpu_usage",
        "memory_usage",
        "alloc_collection_id",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Keep top-level instances only.
    df = df[df["alloc_collection_id"] == 0].copy()

    # Calculate measurement duration.
    df["duration_us"] = df["end_time"] - df["start_time"]

    # Keep intervals of at least 5 minutes.
    minimum_duration_us = 5 * 60 * 1_000_000

    df = df[
        df["duration_us"] >= minimum_duration_us
    ].copy()

    # Remove exact duplicate records.
    df = df.drop_duplicates()

    # Sort chronologically.
    df = df.sort_values(
        by=["start_time", "machine_id", "collection_id"]
    ).reset_index(drop=True)

    return df


if __name__ == "__main__":
    data = load_google_instance_usage()

    print("Google ClusterData loaded successfully.")
    print(f"Rows: {len(data)}")
    print(f"Columns: {len(data.columns)}")
    print(f"Unique machines: {data['machine_id'].nunique()}")
    print(f"Unique collections: {data['collection_id'].nunique()}")
    print(f"Unique instances: {data['instance_index'].nunique()}")
    print(
        f"CPU range: "
        f"{data['cpu_usage'].min()} - "
        f"{data['cpu_usage'].max()}"
    )
    print(
        f"Memory range: "
        f"{data['memory_usage'].min()} - "
        f"{data['memory_usage'].max()}"
    )