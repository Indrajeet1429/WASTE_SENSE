"""
WASTESENSE - Timestamp Processing

Converts Google ClusterData trace timestamps into
useful time representations.

Important:
Google ClusterData timestamps are microseconds from
the beginning of the trace, NOT Unix timestamps.
"""

import pandas as pd


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add time-related features to the dataset.

    Parameters
    ----------
    df : pandas.DataFrame
        Cleaned Google ClusterData.

    Returns
    -------
    pandas.DataFrame
        Dataset with time features.
    """

    data = df.copy()

    # Convert trace timestamp from microseconds to seconds.
    data["timestamp_seconds"] = (
        data["start_time"] / 1_000_000
    )

    # Convert to minutes from the beginning of the trace.
    data["timestamp_minutes"] = (
        data["start_time"] / 1_000_000 / 60
    )

    # Convert to hours from the beginning of the trace.
    data["timestamp_hours"] = (
        data["start_time"] / 1_000_000 / 3600
    )

    # Convert to days from the beginning of the trace.
    data["timestamp_days"] = (
        data["start_time"] / 1_000_000 / 86400
    )

    # Measurement duration in minutes.
    data["duration_minutes"] = (
        data["duration_us"] / 1_000_000 / 60
    )

    # 5-minute bucket number.
    data["time_bucket"] = (
        data["start_time"]
        // (5 * 60 * 1_000_000)
    )

    return data


if __name__ == "__main__":
    from ml.data.loader import load_google_instance_usage

    data = load_google_instance_usage()

    data = add_time_features(data)

    print("WASTESENSE TIMESTAMP PROCESSING")
    print("=" * 40)

    print(f"Rows: {len(data)}")

    print("\nTime range:")
    print(
        f"{data['timestamp_days'].min():.4f} "
        f"to "
        f"{data['timestamp_days'].max():.4f} days"
    )

    print("\nDuration:")
    print(
        f"{data['duration_minutes'].min():.2f} "
        f"to "
        f"{data['duration_minutes'].max():.2f} minutes"
    )

    print("\nTime buckets:")
    print(
        data["time_bucket"].nunique()
    )

    print("\nNew columns:")
    print([
        "timestamp_seconds",
        "timestamp_minutes",
        "timestamp_hours",
        "timestamp_days",
        "duration_minutes",
        "time_bucket",
    ])

    print("\nSample:")
    print(
        data[
            [
                "start_time",
                "timestamp_minutes",
                "timestamp_hours",
                "timestamp_days",
                "duration_minutes",
                "time_bucket",
            ]
        ].head(5).to_string(index=False)
    )