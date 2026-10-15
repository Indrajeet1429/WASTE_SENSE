# WASTESENSE ML Preprocessing

## Purpose

The preprocessing stage prepares Google ClusterData 2019
for feature engineering and machine learning.

## Input

The preprocessing pipeline uses the Google ClusterData
instance usage sample stored in:

`data/raw/google_clusterdata/google_cluster_instance_usage_sample.csv`

## Preprocessing Flow

1. Load the raw dataset using `loader.py`.
2. Verify required columns.
3. Standardize data types.
4. Convert trace timestamps into useful time representations.
5. Validate CPU and memory resource values.
6. Remove invalid records if required.
7. Preserve valid records without unnecessary modification.
8. Generate an intermediate dataset for later ML processing.

## Raw Data Protection

The original dataset in `data/raw/` must never be modified.

All preprocessing operations must create a new DataFrame
or intermediate output.

## Resource Usage

CPU and memory values are kept in the original normalized
form provided by Google ClusterData.

No arbitrary scaling is applied during preprocessing.

## Timestamp Handling

Google ClusterData timestamps represent microseconds
from the beginning of the trace.

They are not Unix timestamps.

The preprocessing pipeline will preserve the original
timestamp and create derived time representations when required.

## Output

The cleaned data will be stored under:

`data/interim/`

The intermediate dataset will be used by subsequent
feature engineering and machine learning stages.