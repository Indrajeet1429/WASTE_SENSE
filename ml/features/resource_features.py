import pandas as pd
import numpy as np


# ============================================================
# STEP 4.4 — ROLLING-WINDOW FEATURES
# ============================================================

def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 15-minute rolling-window features for each machine.

    Each observation represents approximately 5 minutes.
    Therefore, 3 observations represent approximately 15 minutes.
    """

    df = df.copy()

    # Sort chronologically for each machine
    df = df.sort_values(
        ["machine_id", "timestamp_us"]
    ).reset_index(drop=True)

    grouped = df.groupby("machine_id", group_keys=False)

    # --------------------------------------------------------
    # Rolling CPU
    # --------------------------------------------------------

    df["rolling_cpu_mean_15min"] = (
        grouped["actual_cpu"]
        .transform(
            lambda x: x.rolling(3, min_periods=1).mean()
        )
    )

    df["rolling_cpu_max_15min"] = (
        grouped["actual_cpu"]
        .transform(
            lambda x: x.rolling(3, min_periods=1).max()
        )
    )

    # --------------------------------------------------------
    # Rolling Memory
    # --------------------------------------------------------

    df["rolling_memory_mean_15min"] = (
        grouped["actual_memory"]
        .transform(
            lambda x: x.rolling(3, min_periods=1).mean()
        )
    )

    df["rolling_memory_max_15min"] = (
        grouped["actual_memory"]
        .transform(
            lambda x: x.rolling(3, min_periods=1).max()
        )
    )

    # --------------------------------------------------------
    # Rolling CPU utilization
    # --------------------------------------------------------

    df["rolling_cpu_utilization_15min"] = (
        grouped["cpu_utilization"]
        .transform(
            lambda x: x.rolling(3, min_periods=1).mean()
        )
    )

    # --------------------------------------------------------
    # Rolling Memory utilization
    # --------------------------------------------------------

    df["rolling_memory_utilization_15min"] = (
        grouped["memory_utilization"]
        .transform(
            lambda x: x.rolling(3, min_periods=1).mean()
        )
    )

    # --------------------------------------------------------
    # Rolling active tasks
    # --------------------------------------------------------

    df["rolling_active_tasks_15min"] = (
        grouped["active_tasks"]
        .transform(
            lambda x: x.rolling(3, min_periods=1).mean()
        )
    )

    # --------------------------------------------------------
    # CPU variability
    # --------------------------------------------------------

    df["cpu_variability_15min"] = (
        grouped["actual_cpu"]
        .transform(
            lambda x: x.rolling(3, min_periods=1).std()
        )
        .fillna(0)
    )

    # --------------------------------------------------------
    # Memory variability
    # --------------------------------------------------------

    df["memory_variability_15min"] = (
        grouped["actual_memory"]
        .transform(
            lambda x: x.rolling(3, min_periods=1).std()
        )
        .fillna(0)
    )

    # --------------------------------------------------------
    # Rolling overall utilization
    # --------------------------------------------------------

    df["rolling_overall_utilization_15min"] = (
        grouped["overall_utilization"]
        .transform(
            lambda x: x.rolling(3, min_periods=1).mean()
        )
    )

    return df


# ============================================================
# STEP 4.5 — RESOURCE IMBALANCE FEATURES
# ============================================================

def add_imbalance_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add CPU-memory resource imbalance features.
    """

    df = df.copy()

    # --------------------------------------------------------
    # CPU-memory utilization gap
    # --------------------------------------------------------

    df["cpu_memory_utilization_gap"] = (
        df["cpu_utilization"]
        - df["memory_utilization"]
    ).abs()

    # --------------------------------------------------------
    # Total utilization
    # --------------------------------------------------------

    total_utilization = (
        df["cpu_utilization"]
        + df["memory_utilization"]
    )

    # --------------------------------------------------------
    # CPU dominance
    # --------------------------------------------------------

    df["cpu_dominance"] = (
        df["cpu_utilization"]
        / total_utilization.replace(0, pd.NA)
    ).fillna(0)

    # --------------------------------------------------------
    # Memory dominance
    # --------------------------------------------------------

    df["memory_dominance"] = (
        df["memory_utilization"]
        / total_utilization.replace(0, pd.NA)
    ).fillna(0)

    # --------------------------------------------------------
    # Resource balance score
    #
    # 1.0 = balanced
    # 0.0 = highly imbalanced
    # --------------------------------------------------------

    df["resource_balance_score"] = (
        1 - df["cpu_memory_utilization_gap"]
    ).clip(lower=0, upper=1)

    # --------------------------------------------------------
    # CPU-to-memory utilization ratio
    # --------------------------------------------------------

    df["cpu_memory_utilization_ratio"] = (
        df["cpu_utilization"]
        / df["memory_utilization"].replace(0, pd.NA)
    ).fillna(0)

    # --------------------------------------------------------
    # Rolling CPU-memory gap
    # --------------------------------------------------------

    df["rolling_cpu_memory_gap"] = (
        df["rolling_cpu_utilization_15min"]
        - df["rolling_memory_utilization_15min"]
    ).abs()

    # --------------------------------------------------------
    # Rolling resource balance
    # --------------------------------------------------------

    df["rolling_resource_balance"] = (
        1 - df["rolling_cpu_memory_gap"]
    ).clip(lower=0, upper=1)

    # --------------------------------------------------------
    # Headroom imbalance
    # --------------------------------------------------------

    normalized_cpu_headroom = (
        df["cpu_headroom"]
        / df["cpu_capacity"].replace(0, pd.NA)
    )

    normalized_memory_headroom = (
        df["memory_headroom"]
        / df["memory_capacity"].replace(0, pd.NA)
    )

    df["headroom_imbalance"] = (
        normalized_cpu_headroom
        - normalized_memory_headroom
    ).abs().fillna(0)

    return df


# ============================================================
# STEP 4.6 — PERSISTENCE & STABILITY FEATURES
# ============================================================

def add_persistence_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add persistence and stability features.

    IMPORTANT:
    Historical baselines use only previous observations.
    The current observation and future observations are not used
    to calculate its historical baseline.

    This prevents future-information leakage.
    """

    df = df.copy()

    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    df = df.sort_values(
        ["machine_id", "timestamp_us"]
    ).reset_index(drop=True)

    grouped = df.groupby("machine_id", group_keys=False)

    # --------------------------------------------------------
    # 1. CPU change
    # --------------------------------------------------------

    df["cpu_change"] = (
        grouped["actual_cpu"]
        .diff()
        .fillna(0)
    )

    # --------------------------------------------------------
    # 2. Memory change
    # --------------------------------------------------------

    df["memory_change"] = (
        grouped["actual_memory"]
        .diff()
        .fillna(0)
    )

    # --------------------------------------------------------
    # 3. CPU stability over 15 minutes
    # --------------------------------------------------------

    df["cpu_stability_15min"] = (
        grouped["cpu_utilization"]
        .transform(
            lambda x: x.rolling(
                3,
                min_periods=1
            ).std()
        )
        .fillna(0)
    )

    # --------------------------------------------------------
    # 4. Memory stability over 15 minutes
    # --------------------------------------------------------

    df["memory_stability_15min"] = (
        grouped["memory_utilization"]
        .transform(
            lambda x: x.rolling(
                3,
                min_periods=1
            ).std()
        )
        .fillna(0)
    )

    # ========================================================
    # HISTORICAL CPU PERSISTENCE
    # ========================================================

    # Previous observations only.
    #
    # shift(1) removes the current observation before
    # calculating the historical rolling mean.

    cpu_previous_mean = (
        grouped["cpu_utilization"]
        .transform(
            lambda x: x.shift(1).rolling(
                3,
                min_periods=1
            ).mean()
        )
    )

    # For the first observation of each machine there is no
    # historical baseline. We mark it as NaN temporarily.

    cpu_above_previous = pd.Series(
        np.nan,
        index=df.index,
        dtype=float
    )

    valid_cpu_history = cpu_previous_mean.notna()

    cpu_above_previous.loc[valid_cpu_history] = (
        (
            df.loc[valid_cpu_history, "cpu_utilization"]
            >= cpu_previous_mean.loc[valid_cpu_history]
        )
        .astype(float)
    )

    # Rolling persistence based only on current and previous
    # classification values.

    df["cpu_persistence_ratio"] = (
        cpu_above_previous
        .groupby(df["machine_id"])
        .transform(
            lambda x: x.rolling(
                3,
                min_periods=1
            ).mean()
        )
        .fillna(0)
    )

    # ========================================================
    # HISTORICAL MEMORY PERSISTENCE
    # ========================================================

    memory_previous_mean = (
        grouped["memory_utilization"]
        .transform(
            lambda x: x.shift(1).rolling(
                3,
                min_periods=1
            ).mean()
        )
    )

    memory_above_previous = pd.Series(
        np.nan,
        index=df.index,
        dtype=float
    )

    valid_memory_history = memory_previous_mean.notna()

    memory_above_previous.loc[valid_memory_history] = (
        (
            df.loc[
                valid_memory_history,
                "memory_utilization"
            ]
            >= memory_previous_mean.loc[
                valid_memory_history
            ]
        )
        .astype(float)
    )

    df["memory_persistence_ratio"] = (
        memory_above_previous
        .groupby(df["machine_id"])
        .transform(
            lambda x: x.rolling(
                3,
                min_periods=1
            ).mean()
        )
        .fillna(0)
    )

    # ========================================================
    # HISTORICAL OVERALL UTILIZATION PERSISTENCE
    # ========================================================

    overall_previous_mean = (
        grouped["overall_utilization"]
        .transform(
            lambda x: x.shift(1).rolling(
                3,
                min_periods=1
            ).mean()
        )
    )

    overall_above_previous = pd.Series(
        np.nan,
        index=df.index,
        dtype=float
    )

    valid_overall_history = overall_previous_mean.notna()

    overall_above_previous.loc[valid_overall_history] = (
        (
            df.loc[
                valid_overall_history,
                "overall_utilization"
            ]
            >= overall_previous_mean.loc[
                valid_overall_history
            ]
        )
        .astype(float)
    )

    df["overall_persistence_ratio"] = (
        overall_above_previous
        .groupby(df["machine_id"])
        .transform(
            lambda x: x.rolling(
                3,
                min_periods=1
            ).mean()
        )
        .fillna(0)
    )

    # --------------------------------------------------------
    # 8. Workload stability
    # --------------------------------------------------------

    df["workload_stability_15min"] = (
        grouped["active_tasks"]
        .transform(
            lambda x: x.rolling(
                3,
                min_periods=1
            ).std()
        )
        .fillna(0)
    )

    # --------------------------------------------------------
    # 9. Resource stability score
    # --------------------------------------------------------

    total_variability = (
        df["cpu_stability_15min"]
        + df["memory_stability_15min"]
    )

    df["resource_stability_score"] = (
        1 / (1 + total_variability)
    )

    return df


# ============================================================
# STEP 4.7 — FINAL VALIDATION
# ============================================================

def validate_final_features(df: pd.DataFrame) -> bool:
    """
    Perform final validation of the complete feature dataset.
    """

    print("\n" + "=" * 70)
    print("FINAL FEATURE VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Dataset shape
    # --------------------------------------------------------

    print("\n1. Dataset shape:")
    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])

    # --------------------------------------------------------
    # 2. Duplicate rows
    # --------------------------------------------------------

    duplicate_count = df.duplicated().sum()

    print("\n2. Duplicate rows:")
    print(duplicate_count)

    # --------------------------------------------------------
    # 3. Missing values
    # --------------------------------------------------------

    missing_count = df.isnull().sum().sum()

    print("\n3. Total missing values:")
    print(missing_count)

    # --------------------------------------------------------
    # 4. Infinite values
    # --------------------------------------------------------

    numeric_df = df.select_dtypes(
        include=[np.number]
    )

    infinite_count = np.isinf(
        numeric_df
    ).sum().sum()

    print("\n4. Total infinite values:")
    print(infinite_count)

    # --------------------------------------------------------
    # 5. Data types
    # --------------------------------------------------------

    print("\n5. Data types:")
    print(df.dtypes.value_counts())

    # --------------------------------------------------------
    # 6. Unique machines
    # --------------------------------------------------------

    print("\n6. Unique machines:")
    print(df["machine_id"].nunique())

    # --------------------------------------------------------
    # 7. Unique timestamps
    # --------------------------------------------------------

    print("\n7. Unique timestamps:")
    print(df["timestamp_us"].nunique())

    # --------------------------------------------------------
    # 8. Required columns
    # --------------------------------------------------------

    required_columns = [

        # Original / aggregation features
        "timestamp_us",
        "machine_id",
        "cpu_capacity",
        "memory_capacity",
        "active_tasks",
        "actual_cpu",
        "actual_memory",
        "avg_priority",
        "max_priority",
        "cpu_per_task",
        "memory_per_task",
        "cpu_utilization",
        "memory_utilization",

        # Temporal
        "time_bucket_5min",
        "elapsed_minutes",
        "trace_hour",
        "day_of_trace",
        "is_peak_period",

        # Efficiency
        "cpu_headroom",
        "memory_headroom",
        "cpu_efficiency",
        "memory_efficiency",
        "cpu_memory_ratio",
        "normalized_resource_ratio",
        "overall_utilization",
        "resource_imbalance",

        # Workload
        "workload_intensity",
        "cpu_load_per_task",
        "memory_load_per_task",
        "cpu_pressure_per_task",
        "memory_pressure_per_task",
        "priority_weighted_workload",
        "priority_weighted_cpu",
        "priority_weighted_memory",
        "resource_demand_per_task",

        # Rolling
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

        # Imbalance
        "cpu_memory_utilization_gap",
        "cpu_dominance",
        "memory_dominance",
        "resource_balance_score",
        "cpu_memory_utilization_ratio",
        "rolling_cpu_memory_gap",
        "rolling_resource_balance",
        "headroom_imbalance",

        # Persistence
        "cpu_change",
        "memory_change",
        "cpu_stability_15min",
        "memory_stability_15min",
        "cpu_persistence_ratio",
        "memory_persistence_ratio",
        "overall_persistence_ratio",
        "workload_stability_15min",
        "resource_stability_score",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    print("\n8. Required columns missing:")

    if missing_columns:
        print(missing_columns)
    else:
        print("None")

    # --------------------------------------------------------
    # 9. Feature count
    # --------------------------------------------------------

    print("\n9. Total columns:")
    print(len(df.columns))

    # --------------------------------------------------------
    # 10. Numeric sanity check
    # --------------------------------------------------------

    print("\n10. Numeric sanity check:")

    sanity_columns = [
        "active_tasks",
        "cpu_utilization",
        "memory_utilization",
        "overall_utilization",
        "workload_intensity",
        "resource_balance_score",
        "cpu_persistence_ratio",
        "memory_persistence_ratio",
        "overall_persistence_ratio",
        "resource_stability_score",
    ]

    print(
        df[sanity_columns]
        .describe()
        .to_string()
    )

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    validation_passed = (
        duplicate_count == 0
        and missing_count == 0
        and infinite_count == 0
        and len(missing_columns) == 0
    )

    print("\n" + "=" * 70)

    if validation_passed:
        print("FINAL VALIDATION: PASSED")
    else:
        print("FINAL VALIDATION: FAILED")

    print("=" * 70)

    return validation_passed


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    input_file = (
        "data/processed/training/"
        "machine_resource_features_imbalance.csv"
    )

    persistence_output = (
        "data/processed/training/"
        "machine_resource_features_persistence.csv"
    )

    final_output = (
        "data/processed/training/"
        "machine_resource_features_final.csv"
    )

    print("=" * 70)
    print("WASTESENSE — PHASE 4")
    print("CORRECTED PERSISTENCE + FINAL VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load the already validated Step 4.5 dataset
    # --------------------------------------------------------

    print("\nLoading Step 4.5 dataset...")

    df = pd.read_csv(input_file)

    print("Input shape:", df.shape)

    # --------------------------------------------------------
    # Add corrected persistence features
    # --------------------------------------------------------

    print("\nAdding corrected persistence features...")

    df = add_persistence_features(df)

    print(
        "\nPersistence feature dataset shape:",
        df.shape
    )

    # --------------------------------------------------------
    # Persistence feature list
    # --------------------------------------------------------

    persistence_features = [
        "cpu_change",
        "memory_change",
        "cpu_stability_15min",
        "memory_stability_15min",
        "cpu_persistence_ratio",
        "memory_persistence_ratio",
        "overall_persistence_ratio",
        "workload_stability_15min",
        "resource_stability_score",
    ]

    print("\nPersistence features:")

    for feature in persistence_features:
        print(" -", feature)

    # --------------------------------------------------------
    # Check persistence features
    # --------------------------------------------------------

    print("\nPersistence missing values:")

    print(
        df[persistence_features]
        .isnull()
        .sum()
    )

    print("\nPersistence infinite values:")

    print(
        df[persistence_features]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .isnull()
        .sum()
    )

    # --------------------------------------------------------
    # Save persistence dataset
    # --------------------------------------------------------

    df.to_csv(
        persistence_output,
        index=False
    )

    print("\nPersistence dataset saved to:")
    print(persistence_output)

    # --------------------------------------------------------
    # FINAL VALIDATION
    # --------------------------------------------------------

    validation_passed = validate_final_features(df)

    # --------------------------------------------------------
    # Save final dataset only if validation passes
    # --------------------------------------------------------

    if validation_passed:

        df.to_csv(
            final_output,
            index=False
        )

        print("\nFinal dataset saved to:")
        print(final_output)

        print("\n" + "=" * 70)
        print("PHASE 4 FEATURE ENGINEERING: COMPLETE")
        print("=" * 70)

    else:

        print("\nFinal dataset was NOT saved because validation failed.")