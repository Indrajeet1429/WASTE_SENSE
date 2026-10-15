import pandas as pd


def add_efficiency_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add resource-efficiency features to the temporal feature dataset.

    Handles zero-resource rows safely without introducing NaN or
    infinite values into the generated feature columns.
    """

    df = df.copy()

    # CPU headroom: unused CPU capacity
    df["cpu_headroom"] = (
        df["cpu_capacity"] - df["actual_cpu"]
    ).clip(lower=0)

    # Memory headroom: unused memory capacity
    df["memory_headroom"] = (
        df["memory_capacity"] - df["actual_memory"]
    ).clip(lower=0)

    # CPU efficiency relative to capacity
    df["cpu_efficiency"] = (
        1 - df["cpu_utilization"]
    ).clip(lower=0, upper=1)

    # Memory efficiency relative to capacity
    df["memory_efficiency"] = (
        1 - df["memory_utilization"]
    ).clip(lower=0, upper=1)

    # CPU-to-memory usage ratio.
    # When both CPU and memory usage are zero, the ratio is
    # undefined mathematically, so we represent it as 0.
    df["cpu_memory_ratio"] = (
        df["actual_cpu"]
        / df["actual_memory"].replace(0, pd.NA)
    ).fillna(0)

    # Capacity-normalized resource usage
    normalized_cpu = (
        df["actual_cpu"]
        / df["cpu_capacity"].replace(0, pd.NA)
    )

    normalized_memory = (
        df["actual_memory"]
        / df["memory_capacity"].replace(0, pd.NA)
    )

    # When normalized memory usage is zero, the ratio is
    # undefined, so represent it as 0.
    df["normalized_resource_ratio"] = (
        normalized_cpu
        / normalized_memory.replace(0, pd.NA)
    ).fillna(0)

    # Overall resource utilization
    df["overall_utilization"] = (
        df["cpu_utilization"]
        + df["memory_utilization"]
    ) / 2

    # Difference between CPU and memory utilization
    df["resource_imbalance"] = (
        df["cpu_utilization"]
        - df["memory_utilization"]
    ).abs()

    return df


if __name__ == "__main__":
    input_file = (
        "data/processed/training/"
        "machine_resource_features_temporal.csv"
    )

    output_file = (
        "data/processed/training/"
        "machine_resource_features_efficiency.csv"
    )

    df = pd.read_csv(input_file)

    print("Input shape:", df.shape)

    df = add_efficiency_features(df)

    new_features = [
        "cpu_headroom",
        "memory_headroom",
        "cpu_efficiency",
        "memory_efficiency",
        "cpu_memory_ratio",
        "normalized_resource_ratio",
        "overall_utilization",
        "resource_imbalance",
    ]

    print("\nEfficiency features added:")
    print(new_features)

    print("\nOutput shape:", df.shape)

    print("\nSample:")
    print(
        df[
            [
                "machine_id",
                "actual_cpu",
                "cpu_capacity",
                "cpu_utilization",
                "cpu_headroom",
                "cpu_efficiency",
                "memory_utilization",
                "memory_headroom",
                "overall_utilization",
                "resource_imbalance",
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