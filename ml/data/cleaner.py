"""
WASTESENSE - Data Cleaning Pipeline

Cleans the validated Google ClusterData usage dataset
without modifying the original raw CSV.
"""

import pandas as pd

from ml.data.loader import load_google_instance_usage


def clean_usage_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean Google ClusterData usage records.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset loaded by the WASTESENSE loader.

    Returns
    -------
    pandas.DataFrame
        Cleaned dataset.
    """

    data = df.copy()

    # --------------------------------------------------
    # 1. Remove exact duplicate records
    # --------------------------------------------------
    data = data.drop_duplicates().copy()

    # --------------------------------------------------
    # 2. Ensure numeric columns have correct data types
    # --------------------------------------------------
    integer_columns = [
        "start_time",
        "end_time",
        "collection_id",
        "instance_index",
        "machine_id",
        "alloc_collection_id",
        "duration_us",
    ]

    float_columns = [
        "cpu_usage",
        "memory_usage",
    ]

    for column in integer_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    for column in float_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # --------------------------------------------------
    # 3. Remove records with missing required values
    # --------------------------------------------------
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

    data = data.dropna(
        subset=required_columns
    ).copy()

    # --------------------------------------------------
    # 4. Recalculate duration
    # --------------------------------------------------
    data["duration_us"] = (
        data["end_time"] - data["start_time"]
    )

    # --------------------------------------------------
    # 5. Keep valid measurement intervals
    # --------------------------------------------------
    minimum_duration_us = 5 * 60 * 1_000_000

    data = data[
        data["duration_us"] >= minimum_duration_us
    ].copy()

    # --------------------------------------------------
    # 6. Keep top-level instances only
    # --------------------------------------------------
    data = data[
        data["alloc_collection_id"] == 0
    ].copy()

    # --------------------------------------------------
    # 7. Remove invalid timestamps
    # --------------------------------------------------
    data = data[
        data["end_time"] > data["start_time"]
    ].copy()

    # --------------------------------------------------
    # 8. Remove invalid resource values
    # --------------------------------------------------
    data = data[
        (data["cpu_usage"] >= 0)
        & (data["memory_usage"] >= 0)
    ].copy()

    # --------------------------------------------------
    # 9. Sort chronologically
    # --------------------------------------------------
    data = data.sort_values(
        by=[
            "start_time",
            "machine_id",
            "collection_id",
            "instance_index",
        ]
    ).reset_index(drop=True)

    return data


if __name__ == "__main__":
    raw_data = load_google_instance_usage()

    cleaned_data = clean_usage_data(raw_data)

    print("WASTESENSE DATA CLEANING")
    print("=" * 40)

    print(f"Input rows: {len(raw_data)}")
    print(f"Output rows: {len(cleaned_data)}")
    print(f"Rows removed: {len(raw_data) - len(cleaned_data)}")

    print(
        f"Missing values: "
        f"{cleaned_data.isnull().sum().sum()}"
    )

    print(
        f"Duplicate rows: "
        f"{cleaned_data.duplicated().sum()}"
    )

    print(
        f"Negative CPU values: "
        f"{(cleaned_data['cpu_usage'] < 0).sum()}"
    )

    print(
        f"Negative memory values: "
        f"{(cleaned_data['memory_usage'] < 0).sum()}"
    )

    print("\nCleaned columns:")
    print(cleaned_data.columns.tolist())

    print("\nCleaning status:")

    if len(cleaned_data) > 0:
        print("PASSED")
    else:
        print("FAILED - no records remaining")