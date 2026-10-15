"""
WASTESENSE - Data Aggregator

Aggregates Google ClusterData usage records into
5-minute workload-level measurements.
"""

import pandas as pd


def aggregate_usage_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate usage records by machine and 5-minute interval.

    Parameters
    ----------
    df : pandas.DataFrame
        Validated Google ClusterData usage data.

    Returns
    -------
    pandas.DataFrame
        Aggregated workload/resource measurements.
    """

    data = df.copy()

    # Convert trace time from microseconds to seconds.
    data["timestamp_seconds"] = data["start_time"] / 1_000_000

    # Create 5-minute time bucket.
    data["time_bucket"] = (
        (data["start_time"] // (5 * 60 * 1_000_000))
        * (5 * 60)
    )

    # Aggregate resource usage for each machine and time bucket.
    aggregated = (
        data.groupby(
            ["time_bucket", "machine_id"],
            as_index=False
        )
        .agg(
            workload_count=("collection_id", "nunique"),
            instance_count=("instance_index", "nunique"),
            cpu_usage=("cpu_usage", "mean"),
            memory_usage=("memory_usage", "mean"),
            max_cpu_usage=("cpu_usage", "max"),
            max_memory_usage=("memory_usage", "max"),
        )
    )

    # Rename timestamp column.
    aggregated = aggregated.rename(
        columns={
            "time_bucket": "timestamp"
        }
    )

    # Sort chronologically.
    aggregated = aggregated.sort_values(
        ["timestamp", "machine_id"]
    ).reset_index(drop=True)

    return aggregated


if __name__ == "__main__":
    from ml.data.loader import load_google_instance_usage

    data = load_google_instance_usage()

    aggregated_data = aggregate_usage_data(data)

    print("WASTESENSE DATA AGGREGATION")
    print("=" * 40)

    print(f"Input rows: {len(data)}")
    print(f"Output rows: {len(aggregated_data)}")

    print(
        f"Unique machines: "
        f"{aggregated_data['machine_id'].nunique()}"
    )

    print(
        f"Time buckets: "
        f"{aggregated_data['timestamp'].nunique()}"
    )

    print("\nAggregated columns:")
    print(aggregated_data.columns.tolist())

    print("\nFirst 10 rows:")
    print(
        aggregated_data.head(10).to_string(index=False)
    )