"""
WASTESENSE - Dataset Validator

Validates the cleaned Google ClusterData usage dataset
for data quality, resources, workloads, timestamps,
identifiers, and duplicate records.
"""

import pandas as pd


def validate_usage_data(df: pd.DataFrame) -> dict:
    """
    Perform complete validation of Google ClusterData.

    Parameters
    ----------
    df : pandas.DataFrame
        Cleaned Google ClusterData usage data.

    Returns
    -------
    dict
        Complete validation results.
    """

    required_columns = [
        "start_time",
        "end_time",
        "collection_id",
        "instance_index",
        "machine_id",
        "cpu_usage",
        "memory_usage",
        "alloc_collection_id",
        "duration_us",
    ]

    results = {}

    # --------------------------------------------------
    # 1. Required columns
    # --------------------------------------------------
    results["missing_columns"] = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    # Stop detailed validation if required columns are missing.
    if results["missing_columns"]:
        results["valid"] = False
        return results

    # --------------------------------------------------
    # 2. Basic dataset information
    # --------------------------------------------------
    results["total_rows"] = len(df)

    results["unique_machines"] = int(
        df["machine_id"].nunique()
    )

    results["unique_collections"] = int(
        df["collection_id"].nunique()
    )

    results["unique_instances"] = int(
        df["instance_index"].nunique()
    )

    # --------------------------------------------------
    # 3. Missing values
    # --------------------------------------------------
    results["missing_values"] = int(
        df[required_columns].isnull().sum().sum()
    )

    # --------------------------------------------------
    # 4. Duplicate rows
    # --------------------------------------------------
    results["duplicate_rows"] = int(
        df.duplicated().sum()
    )

    # --------------------------------------------------
    # 5. Timestamp validation
    # --------------------------------------------------
    results["invalid_timestamps"] = int(
        (df["end_time"] <= df["start_time"]).sum()
    )

    # --------------------------------------------------
    # 6. Duration validation
    # --------------------------------------------------
    minimum_duration_us = 5 * 60 * 1_000_000

    results["short_intervals"] = int(
        (df["duration_us"] < minimum_duration_us).sum()
    )

    results["invalid_duration"] = int(
        (df["duration_us"] <= 0).sum()
    )

    # --------------------------------------------------
    # 7. CPU validation
    # --------------------------------------------------
    results["negative_cpu"] = int(
        (df["cpu_usage"] < 0).sum()
    )

    results["zero_cpu"] = int(
        (df["cpu_usage"] == 0).sum()
    )

    # Count actual infinite values, separately from missing values.
    results["cpu_infinite_values"] = int(
        df["cpu_usage"].isin([float("inf"), float("-inf")]).sum()
    )
    # Keep the existing result key for compatibility.
    results["cpu_infinite"] = results["cpu_infinite_values"]

    # --------------------------------------------------
    # 8. Memory validation
    # --------------------------------------------------
    results["negative_memory"] = int(
        (df["memory_usage"] < 0).sum()
    )

    results["zero_memory"] = int(
        (df["memory_usage"] == 0).sum()
    )

    results["memory_infinite_values"] = int(
        df["memory_usage"].isin([float("inf"), float("-inf")]).sum()
    )

    # --------------------------------------------------
    # 9. Identifier validation
    # --------------------------------------------------
    results["invalid_machine_ids"] = int(
        (df["machine_id"] <= 0).sum()
    )

    results["invalid_collection_ids"] = int(
        (df["collection_id"] <= 0).sum()
    )

    results["invalid_instance_indexes"] = int(
        (df["instance_index"] < 0).sum()
    )

    # --------------------------------------------------
    # 10. Top-level workload validation
    # --------------------------------------------------
    results["non_top_level"] = int(
        (df["alloc_collection_id"] != 0).sum()
    )

    # --------------------------------------------------
    # 11. Overall validation
    # --------------------------------------------------
    validation_errors = (
        len(results["missing_columns"])
        + results["missing_values"]
        + results["duplicate_rows"]
        + results["invalid_timestamps"]
        + results["short_intervals"]
        + results["invalid_duration"]
        + results["negative_cpu"]
        + results["cpu_infinite_values"]
        + results["negative_memory"]
        + results["memory_infinite_values"]
        + results["invalid_machine_ids"]
        + results["invalid_collection_ids"]
        + results["invalid_instance_indexes"]
        + results["non_top_level"]
    )

    results["validation_errors"] = validation_errors

    results["valid"] = validation_errors == 0

    return results


if __name__ == "__main__":
    from ml.data.loader import load_google_instance_usage
    from ml.data.cleaner import clean_usage_data

    # --------------------------------------------------
    # Load raw/filtered data
    # --------------------------------------------------
    raw_data = load_google_instance_usage()

    # --------------------------------------------------
    # Apply cleaning pipeline
    # --------------------------------------------------
    cleaned_data = clean_usage_data(raw_data)

    # --------------------------------------------------
    # Validate cleaned data
    # --------------------------------------------------
    validation = validate_usage_data(cleaned_data)

    # --------------------------------------------------
    # Display results
    # --------------------------------------------------
    print("WASTESENSE RESOURCE & WORKLOAD VALIDATION")
    print("=" * 50)

    print("\n--- DATASET ---")
    print(f"Total rows: {validation['total_rows']}")
    print(
        f"Unique machines: "
        f"{validation['unique_machines']}"
    )
    print(
        f"Unique collections: "
        f"{validation['unique_collections']}"
    )
    print(
        f"Unique instances: "
        f"{validation['unique_instances']}"
    )

    print("\n--- STRUCTURE ---")
    print(
        f"Missing columns: "
        f"{validation['missing_columns']}"
    )
    print(
        f"Missing values: "
        f"{validation['missing_values']}"
    )
    print(
        f"Duplicate rows: "
        f"{validation['duplicate_rows']}"
    )

    print("\n--- TIMESTAMP & DURATION ---")
    print(
        f"Invalid timestamps: "
        f"{validation['invalid_timestamps']}"
    )
    print(
        f"Short intervals: "
        f"{validation['short_intervals']}"
    )
    print(
        f"Invalid duration: "
        f"{validation['invalid_duration']}"
    )

    print("\n--- CPU ---")
    print(
        f"Negative CPU: "
        f"{validation['negative_cpu']}"
    )
    print(
        f"Zero CPU: "
        f"{validation['zero_cpu']}"
    )
    print(
        f"CPU infinite values: "
        f"{validation['cpu_infinite_values']}"
    )

    print("\n--- MEMORY ---")
    print(
        f"Negative memory: "
        f"{validation['negative_memory']}"
    )
    print(
        f"Zero memory: "
        f"{validation['zero_memory']}"
    )
    print(
        f"Memory infinite values: "
        f"{validation['memory_infinite_values']}"
    )

    print("\n--- IDENTIFIERS ---")
    print(
        f"Invalid machine IDs: "
        f"{validation['invalid_machine_ids']}"
    )
    print(
        f"Invalid collection IDs: "
        f"{validation['invalid_collection_ids']}"
    )
    print(
        f"Invalid instance indexes: "
        f"{validation['invalid_instance_indexes']}"
    )

    print("\n--- WORKLOAD ---")
    print(
        f"Non-top-level records: "
        f"{validation['non_top_level']}"
    )

    print("\n--- FINAL RESULT ---")
    print(
        f"Validation errors: "
        f"{validation['validation_errors']}"
    )

    print("=" * 50)

    if validation["valid"]:
        print("Validation status: PASSED")
    else:
        print("Validation status: FAILED")