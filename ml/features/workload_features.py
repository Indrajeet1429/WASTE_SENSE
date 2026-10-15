import pandas as pd


def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add rolling-window resource features for each machine.

    Rolling features help identify sustained resource usage instead
    of relying only on a single 5-minute observation.
    """

    df = df.copy()

    # Sort chronologically for each machine
    df = df.sort_values(
        ["machine_id", "timestamp_us"]
    ).reset_index(drop=True)

    # ---------------------------------------------------------
    # Rolling window: previous 3 observations
    # 3 observations × 5 minutes = 15 minutes
    # ---------------------------------------------------------

    grouped = df.groupby("machine_id", group_keys=False)

    df["rolling_cpu_mean_15min"] = (
        grouped["actual_cpu"]
        .transform(lambda x: x.rolling(3, min_periods=1).mean())
    )

    df["rolling_cpu_max_15min"] = (
        grouped["actual_cpu"]
        .transform(lambda x: x.rolling(3, min_periods=1).max())
    )

    df["rolling_memory_mean_15min"] = (
        grouped["actual_memory"]
        .transform(lambda x: x.rolling(3, min_periods=1).mean())
    )

    df["rolling_memory_max_15min"] = (
        grouped["actual_memory"]
        .transform(lambda x: x.rolling(3, min_periods=1).max())
    )

    # ---------------------------------------------------------
    # Rolling utilization
    # ---------------------------------------------------------

    df["rolling_cpu_utilization_15min"] = (
        grouped["cpu_utilization"]
        .transform(lambda x: x.rolling(3, min_periods=1).mean())
    )

    df["rolling_memory_utilization_15min"] = (
        grouped["memory_utilization"]
        .transform(lambda x: x.rolling(3, min_periods=1).mean())
    )

    # ---------------------------------------------------------
    # Rolling workload
    # ---------------------------------------------------------

    df["rolling_active_tasks_15min"] = (
        grouped["active_tasks"]
        .transform(lambda x: x.rolling(3, min_periods=1).mean())
    )

    # ---------------------------------------------------------
    # Short-term variability
    # ---------------------------------------------------------

    df["cpu_variability_15min"] = (
        grouped["actual_cpu"]
        .transform(
            lambda x: x.rolling(3, min_periods=1).std()
        )
        .fillna(0)
    )

    df["memory_variability_15min"] = (
        grouped["actual_memory"]
        .transform(
            lambda x: x.rolling(3, min_periods=1).std()
        )
        .fillna(0)
    )

    # ---------------------------------------------------------
    # Rolling resource pressure
    # ---------------------------------------------------------

    df["rolling_overall_utilization_15min"] = (
        grouped["overall_utilization"]
        .transform(lambda x: x.rolling(3, min_periods=1).mean())
    )

    return df


if __name__ == "__main__":

    input_file = (
        "data/processed/training/"
        "machine_resource_features_workload.csv"
    )

    output_file = (
        "data/processed/training/"
        "machine_resource_features_rolling.csv"
    )

    df = pd.read_csv(input_file)

    print("Input shape:", df.shape)

    df = add_rolling_features(df)

    new_features = [
        "rolling_cpu_mean_15min",
        "rolling_cpu_max_15min",
        "rolling_memory_mean_15min",
        "rolling_memory_max_15min",
        "rolling_cpu_utilization_15min",
        "rolling_memory_utilization_15min",
        "rolling_active_tasks_15min",
        "cpu_variability_15min",
        "memory_variability_15min",
        "rolling_overall_utilization_15min",
    ]

    print("\nRolling-window features added:")
    print(new_features)

    print("\nOutput shape:", df.shape)

    print("\nSample:")
    print(
        df[
            [
                "machine_id",
                "timestamp_us",
                "actual_cpu",
                "rolling_cpu_mean_15min",
                "rolling_cpu_max_15min",
                "actual_memory",
                "rolling_memory_mean_15min",
                "rolling_active_tasks_15min",
                "rolling_overall_utilization_15min",
            ]
        ].head(10).to_string(index=False)
    )

    print("\nMissing values:")
    print(df[new_features].isnull().sum())

    print("\nInfinite values:")
    print(
        df[new_features]
        .replace([float("inf"), float("-inf")], pd.NA)
        .isnull()
        .sum()
    )

    df.to_csv(output_file, index=False)

    print("\nSaved to:")
    print(output_file)