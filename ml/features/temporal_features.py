import pandas as pd


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add temporal features to machine-level resource data.

    Google ClusterData timestamps are measured in microseconds
    from the beginning of the trace, not Unix timestamps.
    """

    df = df.copy()

    # Normalize timestamp to a 5-minute bucket
    df["time_bucket_5min"] = (
        df["timestamp_us"] // 300_000_000
    ) * 300_000_000

    # Elapsed time from beginning of trace
    df["elapsed_minutes"] = df["timestamp_us"] / 60_000_000

    # Hour within the trace's repeating 24-hour cycle
    df["trace_hour"] = (
        (df["timestamp_us"] // 3_600_000_000) % 24
    ).astype(int)

    # Day number from beginning of trace
    df["day_of_trace"] = (
        df["timestamp_us"] // 86_400_000_000
    ).astype(int)

    # Peak-period indicator.
    # 08:00–20:00 is treated as the higher-activity period.
    df["is_peak_period"] = (
        (df["trace_hour"] >= 8) &
        (df["trace_hour"] < 20)
    ).astype(int)

    return df


if __name__ == "__main__":
    input_file = "data/processed/training/machine_resource_features.csv"
    output_file = "data/processed/training/machine_resource_features_temporal.csv"

    df = pd.read_csv(input_file)

    print("Input shape:", df.shape)

    df = add_temporal_features(df)

    print("\nTemporal features added:")
    print([
        "time_bucket_5min",
        "elapsed_minutes",
        "trace_hour",
        "day_of_trace",
        "is_peak_period",
    ])

    print("\nOutput shape:", df.shape)

    print("\nSample:")
    print(
        df[
            [
                "timestamp_us",
                "time_bucket_5min",
                "elapsed_minutes",
                "trace_hour",
                "day_of_trace",
                "is_peak_period",
            ]
        ].head(10).to_string(index=False)
    )

    print("\nMissing values:")
    print(
        df[
            [
                "time_bucket_5min",
                "elapsed_minutes",
                "trace_hour",
                "day_of_trace",
                "is_peak_period",
            ]
        ].isnull().sum()
    )

    df.to_csv(output_file, index=False)

    print("\nSaved to:")
    print(output_file)