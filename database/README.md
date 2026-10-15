# WASTESENSE Database

## Overview

The WASTESENSE database stores machine information, workloads, resource measurements, detected waste events, alerts, savings estimates, Waste Replay results, and optimization recommendations.

### Technology Stack

- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- Psycopg 3
- Python

---

## Database Architecture

```text
                         ┌─────────────────┐
                         │     MACHINES    │
                         │   machine_id    │
                         └────────┬────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
           ┌─────────────────┐        ┌─────────────────┐
           │    WORKLOADS    │        │  WASTE EVENTS   │
           │   workload_id   │        │    waste_id     │
           └────────┬────────┘        └────────┬────────┘
                    │                          │
                    ▼                ┌─────────┼─────────┬──────────────┐
        ┌──────────────────────┐     │         │         │              │
        │ RESOURCE             │     ▼         ▼         ▼              ▼
        │ MEASUREMENTS         │   ALERTS    SAVINGS   REPLAY      RECOMMENDATIONS
        └──────────────────────┘
````

---

# Tables

## 1. `machines`

Stores information about compute machines.

| Column            | Type          | Description                     |
| ----------------- | ------------- | ------------------------------- |
| `machine_id`      | BIGINT        | Primary key                     |
| `machine_name`    | VARCHAR(100)  | Unique machine name             |
| `cpu_capacity`    | NUMERIC(12,2) | CPU capacity                    |
| `memory_capacity` | NUMERIC(12,2) | Memory capacity                 |
| `status`          | VARCHAR(20)   | active / inactive / maintenance |
| `created_at`      | TIMESTAMP     | Creation timestamp              |

### Constraints

* Machine name must be unique.
* CPU capacity must be greater than 0.
* Memory capacity must be greater than 0.
* Status must be `active`, `inactive`, or `maintenance`.

---

## 2. `workloads`

Stores workloads executed on machines.

| Column          | Type         | Description               |
| --------------- | ------------ | ------------------------- |
| `workload_id`   | BIGINT       | Primary key               |
| `machine_id`    | BIGINT       | Foreign key to `machines` |
| `workload_type` | VARCHAR(100) | Type of workload          |
| `priority`      | VARCHAR(20)  | Workload priority         |
| `start_time`    | TIMESTAMP    | Workload start time       |
| `end_time`      | TIMESTAMP    | Workload end time         |
| `active_tasks`  | INTEGER      | Number of active tasks    |

### Constraints

* `machine_id` must reference an existing machine.
* Priority must be `low`, `normal`, `high`, or `critical`.
* Active tasks cannot be negative.
* End time cannot be before start time.

---

## 3. `resource_measurements`

Stores actual resource usage measurements.

| Column           | Type          | Description                |
| ---------------- | ------------- | -------------------------- |
| `measurement_id` | BIGINT        | Primary key                |
| `machine_id`     | BIGINT        | Foreign key to `machines`  |
| `workload_id`    | BIGINT        | Foreign key to `workloads` |
| `timestamp`      | TIMESTAMP     | Measurement timestamp      |
| `actual_cpu`     | NUMERIC(12,2) | Actual CPU usage           |
| `actual_memory`  | NUMERIC(12,2) | Actual memory usage        |
| `actual_power`   | NUMERIC(12,2) | Actual power usage         |

### Constraints

* CPU usage cannot be negative.
* Memory usage cannot be negative.
* Power usage cannot be negative.
* `(machine_id, workload_id, timestamp)` must be unique.

---

## 4. `waste_events`

Stores detected resource waste events.

| Column        | Type         | Description                      |
| ------------- | ------------ | -------------------------------- |
| `waste_id`    | BIGINT       | Primary key                      |
| `machine_id`  | BIGINT       | Foreign key to `machines`        |
| `workload_id` | BIGINT       | Foreign key to `workloads`       |
| `timestamp`   | TIMESTAMP    | Detection timestamp              |
| `waste_score` | NUMERIC(5,2) | Waste score from 0 to 100        |
| `severity`    | VARCHAR(20)  | Waste severity                   |
| `waste_type`  | VARCHAR(100) | Type of detected waste           |
| `confidence`  | NUMERIC(5,4) | Detection confidence from 0 to 1 |
| `persistent`  | BOOLEAN      | Whether waste is persistent      |

### Constraints

* Waste score must be between 0 and 100.
* Confidence must be between 0 and 1.
* Severity must be `low`, `medium`, `high`, or `critical`.

---

## 5. `alerts`

Stores alerts generated from waste events.

| Column        | Type         | Description                   |
| ------------- | ------------ | ----------------------------- |
| `alert_id`    | BIGINT       | Primary key                   |
| `waste_id`    | BIGINT       | Foreign key to `waste_events` |
| `severity`    | VARCHAR(20)  | Alert severity                |
| `message`     | VARCHAR(500) | Alert message                 |
| `status`      | VARCHAR(20)  | Alert status                  |
| `created_at`  | TIMESTAMP    | Creation timestamp            |
| `resolved_at` | TIMESTAMP    | Resolution timestamp          |

### Constraints

* Severity must be `low`, `medium`, `high`, or `critical`.
* Status must be `open`, `acknowledged`, or `resolved`.
* Resolution time cannot be before creation time.

---

## 6. `savings`

Stores estimated resource and cost savings.

| Column          | Type          | Description                   |
| --------------- | ------------- | ----------------------------- |
| `saving_id`     | BIGINT        | Primary key                   |
| `waste_id`      | BIGINT        | Foreign key to `waste_events` |
| `cpu_saving`    | NUMERIC(12,2) | Estimated CPU saving          |
| `memory_saving` | NUMERIC(12,2) | Estimated memory saving       |
| `power_saving`  | NUMERIC(12,2) | Estimated power saving        |
| `cost_saving`   | NUMERIC(14,2) | Estimated cost saving         |
| `estimated_at`  | TIMESTAMP     | Estimation timestamp          |

### Relationship

Each waste event can have at most one savings record.

---

## 7. `replay_results`

Stores Waste Replay and counterfactual results.

| Column             | Type          | Description                   |
| ------------------ | ------------- | ----------------------------- |
| `replay_id`        | BIGINT        | Primary key                   |
| `waste_id`         | BIGINT        | Foreign key to `waste_events` |
| `actual_cpu`       | NUMERIC(12,2) | Actual CPU usage              |
| `expected_cpu`     | NUMERIC(12,2) | Expected CPU usage            |
| `actual_power`     | NUMERIC(12,2) | Actual power usage            |
| `expected_power`   | NUMERIC(12,2) | Expected power usage          |
| `estimated_saving` | NUMERIC(14,2) | Estimated saving              |
| `created_at`       | TIMESTAMP     | Creation timestamp            |

### Relationship

Each waste event can have at most one replay result.

---

## 8. `recommendations`

Stores optimization recommendations.

| Column              | Type          | Description                   |
| ------------------- | ------------- | ----------------------------- |
| `recommendation_id` | BIGINT        | Primary key                   |
| `waste_id`          | BIGINT        | Foreign key to `waste_events` |
| `recommendation`    | VARCHAR(1000) | Recommended optimization      |
| `resource`          | VARCHAR(50)   | Target resource               |
| `current_value`     | NUMERIC(12,2) | Current resource value        |
| `suggested_value`   | NUMERIC(12,2) | Suggested resource value      |
| `estimated_benefit` | NUMERIC(14,2) | Estimated benefit             |
| `created_at`        | TIMESTAMP     | Creation timestamp            |

### Relationship

A waste event can have multiple recommendations.

---

# Relationships

```text
machines
   │
   ├──────────────► workloads
   │                    │
   │                    ├──────────────► resource_measurements
   │                    │
   │                    └──────────────► waste_events
   │
   └──────────────► resource_measurements


waste_events
   │
   ├──────────────► alerts
   │
   ├──────────────► savings
   │
   ├──────────────► replay_results
   │
   └──────────────► recommendations
```

---

# Foreign Keys

| Child Table             | Column        | Parent Table   | Parent Column |
| ----------------------- | ------------- | -------------- | ------------- |
| `workloads`             | `machine_id`  | `machines`     | `machine_id`  |
| `resource_measurements` | `machine_id`  | `machines`     | `machine_id`  |
| `resource_measurements` | `workload_id` | `workloads`    | `workload_id` |
| `waste_events`          | `machine_id`  | `machines`     | `machine_id`  |
| `waste_events`          | `workload_id` | `workloads`    | `workload_id` |
| `alerts`                | `waste_id`    | `waste_events` | `waste_id`    |
| `savings`               | `waste_id`    | `waste_events` | `waste_id`    |
| `replay_results`        | `waste_id`    | `waste_events` | `waste_id`    |
| `recommendations`       | `waste_id`    | `waste_events` | `waste_id`    |

---

# SQLAlchemy Structure

Database models are located in:

```text
database/models/
```

Current models:

```text
database/models/
├── __init__.py
├── machine.py
├── workload.py
├── resource_measurement.py
├── waste_event.py
├── alert.py
├── saving.py
├── replay_result.py
└── recommendation.py
```

The SQLAlchemy declarative base and database engine are defined in:

```text
database/base.py
```

The SQLAlchemy session factory is defined in:

```text
database/session.py
```

---

# Alembic Migrations

Alembic configuration:

```text
database/alembic.ini
```

Migration environment:

```text
database/migrations/env.py
```

Migration versions:

```text
database/migrations/versions/
```

## Create a migration

```powershell
python -m alembic -c database\alembic.ini revision --autogenerate -m "description"
```

## Apply migrations

```powershell
python -m alembic -c database\alembic.ini upgrade head
```

## Check current migration

```powershell
python -m alembic -c database\alembic.ini current
```

The initial WASTESENSE schema migration creates all eight application tables.

---

# Demo Data

Demo data is generated using:

```powershell
python -m database.seeds.seed_demo
```

The seed creates a complete example flow:

```text
Machine
   ↓
Workload
   ↓
Resource Measurements
   ↓
Waste Event
   ├── Alert
   ├── Saving
   ├── Replay Result
   └── Recommendation
```

The demo machine is:

```text
demo-linuxone-01
```

The seed script checks whether the demo machine already exists before inserting duplicate demo data.

---

# Testing

Database integration tests are located in:

```text
tests/test_database_integration.py
```

Run the database integration test:

```powershell
python -m pytest tests/test_database_integration.py -v
```

The integration test verifies:

* SQLAlchemy database session
* PostgreSQL connectivity
* Machine insertion
* Workload insertion
* Resource measurement insertion
* Waste event insertion
* Foreign-key relationships
* Database constraints
* Transaction rollback

Test transactions are rolled back so the integration test does not leave test records in the database.

---

# Environment Configuration

Database configuration is stored locally in `.env`.

Example:

```text
DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/wastesense
DATABASE_PASSWORD=<YOUR_POSTGRES_PASSWORD>
```

## Security

* Never commit `.env`.
* Never commit real database passwords.
* Use `.env.example` as the configuration template.
* Production credentials must be managed through secure environment variables or secrets management.

---

# Current Database Status

The WASTESENSE PostgreSQL database has been successfully:

* Installed
* Configured
* Connected to SQLAlchemy
* Modeled using SQLAlchemy ORM
* Migrated using Alembic
* Verified directly in PostgreSQL
* Tested using an integration test
* Populated with demo data

The database is ready for FastAPI backend integration.



