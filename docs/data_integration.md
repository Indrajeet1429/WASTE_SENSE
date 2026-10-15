WASTESENSE/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── pyproject.toml
├── uv.lock
│
├── config/
│   ├── settings.yaml
│   ├── model_config.yaml
│   └── logging.yaml
│
├── data/
│   ├── README.md
│   ├── raw/
│   │   ├── google_clusterdata/
│   │   ├── google_powerdata/
│   │   └── alibaba_clusterdata/
│   ├── interim/
│   ├── processed/
│   │   ├── training/
│   │   ├── validation/
│   │   └── testing/
│   └── samples/
│       └── demo_dataset.parquet
│
├── ml/
│   ├── __init__.py
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── cleaner.py
│   │   ├── validator.py
│   │   └── aggregator.py
│   │
│   ├── features/
│   │   ├── __init__.py
│   │   ├── workload_features.py
│   │   ├── resource_features.py
│   │   ├── efficiency_features.py
│   │   └── temporal_features.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── expected_resource.py
│   │   ├── anomaly_detector.py
│   │   └── model_loader.py
│   │
│   ├── intelligence/
│   │   ├── __init__.py
│   │   ├── waste_score.py
│   │   ├── fingerprint.py
│   │   ├── persistence.py
│   │   ├── root_cause.py
│   │   ├── savings.py
│   │   ├── replay.py
│   │   ├── optimization.py
│   │   └── recommendation.py
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── preprocess.py
│   │   ├── predict.py
│   │   └── analyze.py
│   │
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── metrics.py
│   │   ├── waste_injection.py
│   │   └── evaluate.py
│   │
│   └── artifacts/
│       ├── models/
│       ├── preprocessors/
│       └── metadata/
│
├── database/
│   ├── README.md
│   ├── alembic.ini
│   ├── migrations/
│   │   ├── env.py
│   │   └── versions/
│   └── seeds/
│       └── demo_data.sql
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── worker.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── overview.py
│   │   ├── machines.py
│   │   ├── workloads.py
│   │   ├── waste.py
│   │   ├── alerts.py
│   │   ├── trends.py
│   │   ├── savings.py
│   │   ├── replay.py
│   │   └── optimization.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ml_service.py
│   │   ├── waste_service.py
│   │   ├── analytics_service.py
│   │   └── monitoring_service.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── machine_repository.py
│   │       ├── workload_repository.py
│   │       ├── resource_repository.py
│   │       ├── waste_repository.py
│   │       ├── alert_repository.py
│   │       └── analytics_repository.py
│   │
│   └── core/
│       ├── __init__.py
│       ├── config.py
│       ├── logging.py
│       └── security.py
│
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── index.html
│   │
│   ├── public/
│   │
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       │
│       ├── components/
│       │   ├── common/
│       │   ├── cards/
│       │   ├── charts/
│       │   ├── tables/
│       │   └── alerts/
│       │
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   ├── Machines.jsx
│       │   ├── MachineDetails.jsx
│       │   ├── WasteEvents.jsx
│       │   ├── WasteDetails.jsx
│       │   ├── Trends.jsx
│       │   ├── Alerts.jsx
│       │   ├── Replay.jsx
│       │   ├── Optimization.jsx
│       │   └── Savings.jsx
│       │
│       ├── services/
│       │   └── api.js
│       │
│       ├── hooks/
│       ├── utils/
│       └── styles/
│
├── scripts/
│   ├── setup.sh
│   ├── prepare_data.py
│   ├── train_models.py
│   ├── evaluate_models.py
│   ├── import_data.py
│   └── health_check.py
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_analysis.ipynb
│   ├── 03_model_development.ipynb
│   ├── 04_anomaly_analysis.ipynb
│   └── 05_model_evaluation.ipynb
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_features.py
│   │   ├── test_scoring.py
│   │   ├── test_fingerprint.py
│   │   ├── test_persistence.py
│   │   ├── test_replay.py
│   │   └── test_optimization.py
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_ml_pipeline.py
│   │   ├── test_database.py
│   │   └── test_api.py
│   │
│   └── fixtures/
│       └── sample_data/
│
├── deployment/
│   ├── nginx/
│   │   └── wastesense.conf
│   │
│   ├── systemd/
│   │   ├── wastesense-api.service
│   │   └── wastesense-worker.service
│   │
│   ├── postgres/
│   │   └── backup.sh
│   │
│   └── scripts/
│       ├── deploy.sh
│       ├── start.sh
│       ├── stop.sh
│       ├── restart.sh
│       └── health_check.sh
│
├── logs/
│   ├── .gitkeep
│   ├── api/
│   ├── worker/
│   └── ml/
│
└── docs/
    ├── architecture.md
    ├── data_dictionary.md
    ├── data_integration.md
    ├── ml_pipeline.md
    ├── database_design.md
    ├── api_documentation.md
    ├── deployment.md
    ├── testing.md
    └── demo_guide.md


==================================================
WASTESENSE — PROJECT STATUS
==================================================

PROJECT:
WasteSense — AI/ML-Based Intelligent Resource Waste Detection

CORE OBJECTIVE:
Detect hidden resource inefficiency by comparing actual resource
consumption with the expected resource consumption for the amount
and type of work being performed.

Example:

1000 tasks + 20% CPU
→ potentially normal

20 tasks + 80% CPU
→ potentially inefficient

The system should therefore NOT simply classify high CPU or memory
usage as waste.

Instead:

Workload Characteristics
        ↓
Expected Resource Usage
        ↓
Actual Resource Usage
        ↓
Expected vs Actual
        ↓
Residual Calculation
        ↓
Anomaly Detection
        ↓
Waste Score
        ↓
Waste Fingerprint
        ↓
Persistence Detection
        ↓
Root Cause Analysis
        ↓
Savings Estimation
        ↓
Waste Replay
        ↓
Optimization Recommendation
        ↓
Dashboard / Alerts


==================================================
MUST-HAVE FEATURES
==================================================

1. Expected Resource Prediction
2. Waste Detection
3. Waste Score
4. Waste Fingerprint
5. Root-Cause Explanation
6. Waste Replay
7. Waste Trends / History
8. Persistent Waste Alerts
9. Potential Resource / Power Savings Estimate
10. What-If Optimization / Recommendation


==================================================
FEATURES NOT REQUIRED
==================================================

Do NOT add unnecessary complexity such as:

- LLM chatbot
- Mobile application
- Kubernetes
- Kafka
- Redis
- Blockchain
- Microservices
- Computer Vision
- Generative AI
- Multiple redundant ML models
- Reinforcement Learning unless specifically required later


==================================================
DATASETS
==================================================

PRIMARY DATASETS:

1. Google ClusterData 2019
2. Google PowerData 2019

VALIDATION DATASET:

3. Alibaba ClusterData 2018

OPTIONAL:

4. Bitbrains


IMPORTANT:

Google ClusterData 2019 is very large, approximately 2.4 TiB
compressed.

Do NOT download the complete dataset locally.

Use BigQuery to query only the required subset and export the
manageable processed data.

Google ClusterData 2019:

- 8 Borg cells
- May 2019 trace
- Contains workload/resource information
- Includes 5-minute CPU usage/resource measurements

Google PowerData 2019:

- Contains power utilization information
- Power measurements are organized around power domains/PDU data


==================================================
GOOGLE CLUSTERDATA 2019
==================================================

Official BigQuery project:

google.com:google-cluster-data

Datasets:

clusterdata_2019_a
clusterdata_2019_b
clusterdata_2019_c
clusterdata_2019_d
clusterdata_2019_e
clusterdata_2019_f
clusterdata_2019_g
clusterdata_2019_h


IMPORTANT TABLES:

machine_events

Important fields:

- machine_id
- capacity.cpus
- capacity.memory


instance_usage

Important fields:

- start_time
- end_time
- collection_id
- instance_index
- machine_id
- average_usage.cpus
- average_usage.memory
- alloc_collection_id


instance_events

Important fields:

- collection_id
- instance_index
- machine_id
- priority
- alloc_collection_id


IMPORTANT:

Google ClusterData timestamps are measured in microseconds from
the beginning of the trace.

They are NOT Unix epoch timestamps.


==================================================
OFFICIAL INSTANCE USAGE QUERY PATTERN
==================================================

SELECT
    CAST(
        FLOOR(start_time / (1e6 * 300))
        * (1000000 * 300)
        AS INT64
    ) AS time,

    collection_id,
    instance_index,
    machine_id,

    average_usage.cpus AS cpu_usage,
    average_usage.memory AS memory_usage

FROM
    `google.com:google-cluster-data`.
    clusterdata_2019_{cell}.instance_usage

WHERE
    (alloc_collection_id IS NULL OR alloc_collection_id = 0)

    AND
    (end_time - start_time) >=
    (5 * 60 * 1e6);


==================================================
FINAL DATA INTEGRATION
==================================================

The integrated dataset was created using:

Google ClusterData 2019
        ↓
Instance Usage
        ↓
Machine Capacity
        ↓
Workload Priority
        ↓
Machine-Level Aggregation
        ↓
Feature Engineering
        ↓
Google PowerData 2019
        ↓
Machine → PDU Mapping
        ↓
Final Integrated Dataset


==================================================
FINAL BIGQUERY TABLE
==================================================

wastesense.wastesense_data.machine_resource_features_final_power_pdu


==================================================
FINAL LOCAL DATASET
==================================================

data/processed/training/machine_resource_features_final_power_pdu.csv


==================================================
POWER DATA INTERPRETATION
==================================================

IMPORTANT:

The power value in the final dataset represents PDU-level measured
power utilization associated with the machine through the
machine-to-PDU mapping.

It MUST NOT be described as direct per-machine watt consumption.

Therefore:

CORRECT:
"PDU-level measured power utilization associated with the machine."

INCORRECT:
"Exact power consumed by the individual machine in watts."


==================================================
TARGET DATA STRUCTURE
==================================================

The integrated dataset should contain information corresponding
to the following concepts:

timestamp
machine_id
active_tasks
priority
cpu_capacity
memory_capacity
actual_cpu
actual_memory
power


==================================================
DERIVED FEATURES
==================================================

Important derived features include:

cpu_per_task
memory_per_task
power_per_task
rolling_cpu
rolling_memory
rolling_power
workload_duration


Additional features may be created when supported by the data and
required by the ML pipeline.


==================================================
ML PIPELINE
==================================================

PHASE 1:
Data Acquisition

PHASE 2:
Data Cleaning / Preparation

PHASE 3:
Resource Aggregation

PHASE 4:
Feature Engineering

PHASE 5:
Expected Resource Modeling

PHASE 6:
Anomaly Detection

PHASE 7:
Waste Intelligence

PHASE 8:
Evaluation

PHASE 9:
Backend Integration

PHASE 10:
Frontend Dashboard


==================================================
CURRENT STATUS
==================================================

Phase 1 — Data Acquisition
COMPLETE

Phase 2 — Data Cleaning / Preparation
COMPLETE

Phase 3 — Resource Aggregation
COMPLETE

Phase 4 — Feature Engineering
COMPLETE

Google PowerData Integration
COMPLETE

Machine → PDU Integration
COMPLETE

Final Validation
PASSED

CURRENT PHASE:

PHASE 5 — EXPECTED RESOURCE MODELING


==================================================
PHASE 5 — EXPECTED RESOURCE MODEL
==================================================

The model must learn normal/expected resource usage based on
workload and system characteristics.

Expected outputs may include:

expected_cpu
expected_memory
expected_power


The fundamental comparison is:

actual_resource - expected_resource = residual/excess


For example:

Actual CPU     = 80%
Expected CPU   = 35%

CPU Excess     = 45%


The system should use this residual to identify abnormal
resource behavior rather than using raw CPU usage alone.


==================================================
EXPECTED RESOURCE MODELING
==================================================

Possible model families:

- Gradient Boosting
- Random Forest Regressor
- XGBoost Regressor
- LightGBM if available
- Other suitable regression models


Do NOT unnecessarily train many models.

Start with a strong baseline and compare only useful alternatives.


Evaluation metrics:

- MAE
- RMSE
- R²


Separate models may be trained for:

CPU
Memory
Power


OR a suitable multi-output approach may be used if justified.


==================================================
ANOMALY DETECTION
==================================================

Recommended anomaly detector:

Isolation Forest


IMPORTANT:

Isolation Forest should NOT be the only intelligence layer.

The primary concept is:

Expected Resource Model
        +
Residual Analysis
        +
Anomaly Detection


Example:

Actual CPU = 80
Expected CPU = 35

Residual = 45

If the residual is unusually high and persists over time,
the event can be classified as resource waste.


==================================================
WASTE SCORE
==================================================

The Waste Score should combine relevant signals such as:

- CPU excess
- Memory excess
- Power excess
- Anomaly strength
- Persistence
- Workload characteristics


The final score can be normalized to:

0–100


Example interpretation:

0–30
NORMAL

31–60
LOW WASTE

61–80
MEDIUM WASTE

81–100
HIGH WASTE


These thresholds should be configurable rather than hard-coded
throughout the application.


==================================================
WASTE FINGERPRINT
==================================================

Waste Fingerprint identifies the dominant type/pattern of waste.

Possible examples:

CPU_INEFFICIENCY
MEMORY_INEFFICIENCY
POWER_INEFFICIENCY
CPU_AND_POWER_INEFFICIENCY
MEMORY_AND_POWER_INEFFICIENCY
SUSTAINED_RESOURCE_WASTE
BURST_RESOURCE_WASTE


The fingerprint should be generated from the actual signals and
not randomly assigned.


==================================================
PERSISTENCE
==================================================

Temporary spikes should not automatically be treated as
persistent waste.

The system should distinguish:

Transient anomaly
from
Sustained anomaly


Persistence should consider consecutive observations or an
appropriate rolling time window.


Example:

One abnormal point
→ transient

Abnormal behavior across many consecutive observations
→ persistent


Persistent waste should have higher importance than a short spike.


==================================================
ROOT CAUSE ANALYSIS
==================================================

Root Cause Analysis should identify which input features contributed
most strongly to the predicted expected-vs-actual deviation or
waste classification.


Possible methods:

- Feature importance
- SHAP
- Model-specific explanations


IMPORTANT:

Feature contribution is NOT automatically causal proof.

Therefore the UI/report should use wording such as:

"Likely contributing factors"

rather than:

"Confirmed cause"


Example:

Likely contributing factors:

1. High CPU per task
2. Low active workload
3. High priority workload
4. Sustained CPU excess


==================================================
WASTE REPLAY
==================================================

Waste Replay is a model-based counterfactual simulation.

It should allow the user to examine:

Actual resource behavior
versus
Estimated behavior under a more efficient condition.


Example:

Current:

CPU = 80%
Memory = 50%
Power = 200

Estimated efficient condition:

CPU = 40%
Memory = 45%
Power = 150


The result should be clearly marked as:

MODEL-BASED ESTIMATE


It must NOT be presented as guaranteed real-world savings.


==================================================
SAVINGS ESTIMATION
==================================================

Potential savings may include:

CPU resource reduction
Memory resource reduction
Potential power reduction


Example:

Current CPU:
80%

Expected CPU:
40%

Potential excess:
40 percentage points


For power:

Current associated PDU power:
200

Estimated efficient level:
150

Potential reduction:
50 power units


The exact physical energy/cost interpretation must depend on
the available power data and its documented meaning.


==================================================
WHAT-IF OPTIMIZATION
==================================================

The initial implementation should use:

Expected-resource model
+
Counterfactual analysis
+
Constraints


Do NOT start with Reinforcement Learning.


Example:

"What happens if workload/resource allocation is changed?"


The system can estimate expected resource behavior under
different workload conditions.


==================================================
RECOMMENDATION ENGINE
==================================================

Recommendations should be generated from detected waste patterns.

Examples:

CPU inefficiency:
"Investigate high CPU usage relative to active workload."

Memory inefficiency:
"Review memory allocation and workload memory requirements."

Power inefficiency:
"Investigate sustained resource usage associated with elevated
PDU-level power utilization."

Persistent waste:
"Prioritize this workload for optimization because the anomaly
persists across multiple observations."


Recommendations should be evidence-based and tied to the detected
fingerprint.


==================================================
MODEL EVALUATION
==================================================

Evaluation should include controlled waste injection into real
trace data.

Synthetic waste can be introduced into otherwise normal records.

Because the injected waste is known, synthetic ground-truth labels
can be created.


Useful metrics:

- Precision
- Recall
- F1-score
- False Positive Rate
- Detection Latency
- Waste Estimation Error


Example:

Normal trace
        ↓
Inject controlled CPU waste
        ↓
Run WasteSense
        ↓
Compare detected waste
with
known injected waste


This provides a measurable evaluation framework.


==================================================
CROSS-DATASET VALIDATION
==================================================

After the primary Google dataset pipeline is working:

Use Alibaba ClusterData 2018 as an external validation dataset
where compatible features are available.


Purpose:

Test whether the waste-detection methodology generalizes beyond
the training dataset.


Do NOT assume that the datasets have identical schemas.


Create a compatible feature mapping first.


==================================================
STABLE ML INTERFACE
==================================================

The ML system should expose a stable interface:

result = analyze_workload(input_data)


The rest of the backend should depend on this interface rather
than directly depending on individual ML implementation details.


Expected result structure:

{
    "machine_id": "M102",
    "timestamp": "2026-10-07T14:30:00",

    "actual": {
        "cpu": 71.0,
        "memory": 47.0,
        "power": 190.0
    },

    "expected": {
        "cpu": 34.0,
        "memory": 44.0,
        "power": 145.0
    },

    "excess": {
        "cpu": 37.0,
        "memory": 3.0,
        "power": 45.0
    },

    "waste": {
        "score": 87,
        "severity": "HIGH",
        "type": "CPU_INEFFICIENCY",
        "confidence": 0.91,
        "persistent": true
    },

    "root_cause": [],

    "savings": {},

    "replay": {},

    "recommendations": []
}


NOTE:

The numerical values above are illustrative examples only.

They are NOT actual dataset results.


==================================================
RECOMMENDED ML FILE RESPONSIBILITIES
==================================================

ml/data/loader.py
→ Load raw and processed data.

ml/data/cleaner.py
→ Data cleaning.

ml/data/validator.py
→ Schema, missing-value and quality validation.

ml/data/aggregator.py
→ Workload/machine-level aggregation.

ml/features/workload_features.py
→ Workload-related features.

ml/features/resource_features.py
→ CPU, memory and power features.

ml/features/efficiency_features.py
→ Per-task and efficiency features.

ml/features/temporal_features.py
→ Rolling/time-related features.

ml/models/expected_resource.py
→ Train/load expected-resource models.

ml/models/anomaly_detector.py
→ Isolation Forest and anomaly scoring.

ml/models/model_loader.py
→ Load trained model artifacts.

ml/intelligence/waste_score.py
→ Waste score calculation.

ml/intelligence/fingerprint.py
→ Waste type/fingerprint.

ml/intelligence/persistence.py
→ Persistent anomaly detection.

ml/intelligence/root_cause.py
→ Feature contribution / explanation.

ml/intelligence/savings.py
→ Potential savings estimation.

ml/intelligence/replay.py
→ Counterfactual waste replay.

ml/intelligence/optimization.py
→ What-if optimization.

ml/intelligence/recommendation.py
→ Evidence-based recommendations.

ml/pipeline/preprocess.py
→ Production preprocessing.

ml/pipeline/predict.py
→ Expected resource prediction.

ml/pipeline/analyze.py
→ Complete WasteSense analysis pipeline.

ml/evaluation/metrics.py
→ Evaluation metrics.

ml/evaluation/waste_injection.py
→ Controlled waste injection.

ml/evaluation/evaluate.py
→ Complete evaluation workflow.


==================================================
TEAM STRUCTURE
==================================================

MEMBER 1 — ML / AI
Branch:
member1-ml

Owns:

ml/
scripts/train_models.py
ML notebooks


MEMBER 2 — PostgreSQL Database
Branch:
member2-database

Owns:

database/


MEMBER 3 — Monitoring Frontend
Branch:
member3-monitoring-ui

Owns:

Dashboard
Machines
Machine Details
Monitoring charts
Monitoring components


MEMBER 4 — Intelligence Frontend
Branch:
member4-intelligence-ui

Owns:

Waste Events
Waste Details
Trends
Alerts
Replay
Optimization
Savings


MEMBER 5 — FastAPI + ML Integration
Branch:
member5-backend-ml

Owns:

backend/api/
backend/services/ml_service.py
backend main integration


MEMBER 6 — Backend + Database Integration
Branch:
member6-backend-db

Owns:

backend/db/
repositories
analytics services
database integration


==================================================
DATABASE RESPONSIBILITY
==================================================

The PostgreSQL database should store application-level data
required by the backend and dashboard.

Suggested conceptual entities:

Machines
Workloads
Resource Observations
Waste Events
Alerts
Waste Trends
Savings Estimates
Replay Results
Optimization Results


The exact schema should be designed by the database member based
on the final ML output and API requirements.


==================================================
BACKEND RESPONSIBILITY
==================================================

FastAPI provides the API layer between:

Frontend
    ↕
FastAPI
    ↕
ML Services / Database


Main API areas:

Overview
Machines
Workloads
Waste
Alerts
Trends
Savings
Replay
Optimization


The backend should NOT duplicate ML calculations.

ML calculations should remain inside the ML/service layer.


==================================================
FRONTEND RESPONSIBILITY
==================================================

Main pages:

Dashboard
Machines
Machine Details
Waste Events
Waste Details
Trends
Alerts
Replay
Optimization
Savings


Dashboard should communicate the main project idea immediately:

Actual Usage
vs
Expected Usage
vs
Detected Waste


Important dashboard information:

- Current waste score
- Active waste events
- Persistent waste
- CPU excess
- Memory excess
- Associated power utilization
- Potential savings
- Recent alerts
- Waste trend


==================================================
WASTESENSE DASHBOARD CONCEPT
==================================================

Dashboard:

--------------------------------------------------
WASTESENSE
Intelligent Resource Waste Detection
--------------------------------------------------

Overall Waste Score

        72 / 100

--------------------------------------------------

CPU
Actual:       78%
Expected:     39%
Excess:       +39%

Memory
Actual:       54%
Expected:     46%
Excess:       +8%

Power
Associated PDU:
Actual:       190
Expected:     148
Excess:       +42

--------------------------------------------------

Persistent Waste:
YES

Fingerprint:
CPU_INEFFICIENCY

Likely Contributors:
- High CPU per task
- Low active workload
- Sustained CPU excess

Potential Savings:
Model-based estimate

--------------------------------------------------

Recent Waste Events
--------------------------------------------------

Machine     Score     Type                 Status

M102        87        CPU_INEFFICIENCY     Persistent
M205        73        POWER_INEFFICIENCY   Persistent
M118        52        MEMORY_INEFFICIENCY  Transient


==================================================
GIT WORKFLOW
==================================================

main
│
├── member1-ml
├── member2-database
├── member3-monitoring-ui
├── member4-intelligence-ui
├── member5-backend-ml
└── member6-backend-db


Each member should work only on their assigned area wherever
possible.

Changes should be merged into the main branch after testing.


==================================================
IMPORTANT DATA RULES
==================================================

1. Do NOT download the entire Google ClusterData 2019 dataset.

2. Use BigQuery to extract only required data.

3. Keep raw data separate from processed data.

4. Never overwrite raw data during preprocessing.

5. Keep training, validation and testing datasets separated.

6. Document all transformations.

7. Maintain reproducibility of feature engineering.

8. Validate schema before model training.

9. Avoid data leakage.

10. Expected-resource models must be trained only using appropriate
training data.

11. Test data must remain unseen during model fitting.

12. Do not treat PDU-level power as direct per-machine watt
consumption.

13. Do not claim model-based savings as guaranteed real-world
savings.

14. Do not call feature importance a confirmed causal explanation.


==================================================
REPRODUCIBILITY
==================================================

The final integrated dataset was created using BigQuery and:

Google ClusterData 2019
+
Google PowerData 2019


Integration:

Google ClusterData instance_usage
        ↓
Machine capacity
        ↓
Workload priority
        ↓
Machine-level aggregation
        ↓
Feature engineering
        ↓
Google PowerData
        ↓
Machine → PDU mapping
        ↓
Final integrated dataset


Final BigQuery table:

wastesense.wastesense_data.machine_resource_features_final_power_pdu


Final local dataset:

data/processed/training/machine_resource_features_final_power_pdu.csv


==================================================
CURRENT NEXT STEP
==================================================

PHASE 5 — EXPECTED RESOURCE MODELING


The immediate next task is:

1. Load the final integrated dataset.

2. Validate columns and data types.

3. Inspect distributions.

4. Identify the input features.

5. Define target resource variables.

6. Split data appropriately into training and testing data.

7. Train a baseline expected-resource model.

8. Evaluate using MAE, RMSE and R².

9. Compare actual versus expected resources.

10. Calculate residuals.

11. Save the trained model and preprocessing artifacts.

12. Prepare the output for the anomaly-detection stage.


The next major pipeline will be:

FINAL DATASET
      ↓
PREPROCESSING
      ↓
EXPECTED CPU MODEL
      ↓
EXPECTED MEMORY MODEL
      ↓
EXPECTED POWER MODEL
      ↓
ACTUAL vs EXPECTED
      ↓
RESIDUALS
      ↓
ISOLATION FOREST
      ↓
WASTE SCORE
      ↓
FINGERPRINT
      ↓
PERSISTENCE
      ↓
ROOT CAUSE
      ↓
SAVINGS
      ↓
REPLAY
      ↓
OPTIMIZATION
      ↓
FASTAPI
      ↓
POSTGRESQL
      ↓
REACT DASHBOARD