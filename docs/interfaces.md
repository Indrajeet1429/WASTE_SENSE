```markdown
# WASTESENSE Shared Interfaces

## 1. Purpose

This document defines the common interfaces between the ML, Backend, Database, and Frontend components of WASTESENSE.

All team members must follow these contracts during development.

---

## 2. ML Interface

The main ML entry point is:

```python
result = analyze_workload(input_data)
```

### Input

```json
{
  "machine_id": "M102",
  "timestamp": "2026-10-07T14:30:00",
  "active_tasks": 20,
  "workload_type": "COMPUTE",
  "priority": 1,
  "workload_duration": 120,
  "cpu_capacity": 100,
  "memory_capacity": 100,
  "actual_cpu": 71.0,
  "actual_memory": 47.0,
  "actual_power": 190.0
}
```

### Output

```json
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
```

---

## 3. Waste Severity

Allowed values:

- LOW
- MEDIUM
- HIGH
- CRITICAL

---

## 4. Waste Types

Initial allowed waste types:

- CPU_INEFFICIENCY
- MEMORY_INEFFICIENCY
- POWER_INEFFICIENCY
- IDLE_RESOURCE
- OVERPROVISIONING
- RESOURCE_MISMATCH
- SUSTAINED_WASTE
- MIXED_RESOURCE_WASTE

More types may be added only after team discussion.

---

## 5. Backend API

The backend will expose REST APIs under:

```text
/api
```

### API Endpoints

```text
GET /api/overview

GET /api/machines

GET /api/machines/{machine_id}

GET /api/workloads

GET /api/waste

GET /api/waste/{waste_id}

GET /api/alerts

GET /api/trends

GET /api/savings

GET /api/replay/{waste_id}

POST /api/optimization
```

---

## 6. Database Responsibility

The database stores:

- machines
- workloads
- resource measurements
- waste events
- alerts
- savings estimates
- replay results
- recommendations

Database implementation is owned by the database members.

---

## 7. Frontend Responsibility

Frontend consumes backend APIs.

Frontend should NOT directly access PostgreSQL.

Architecture:

```text
React
  ↓
FastAPI
  ↓
Services
  ↓
PostgreSQL / ML
```

---

## 8. Mock Data Rule

If another member's component is not ready, use mock data following this document.

Do not create a new incompatible data format.

---

## 9. Ownership

### Member 1 – ML

Branch:

```text
member1-ml
```

Responsibilities:

- ML data processing
- Feature engineering
- Expected resource prediction
- Anomaly detection
- Waste score
- Waste fingerprint
- Persistence detection
- Root cause analysis
- Savings estimation
- Waste Replay
- Optimization
- Recommendations
- ML evaluation

Main folders:

```text
ml/
scripts/train_models.py
```

---

### Member 2 – Database

Branch:

```text
member2-database
```

Responsibilities:

- PostgreSQL database design
- Database models
- Alembic migrations
- Database repositories
- Database seed/demo data
- Database documentation

Main folders:

```text
database/
backend/db/
```

---

### Member 3 – Monitoring UI

Branch:

```text
member3-monitoring-ui
```

Responsibilities:

- Monitoring dashboard
- Machine monitoring
- Machine details
- Resource usage charts
- Waste event monitoring
- Alerts interface
- Trends/history interface

Main folders:

```text
frontend/
```

---

### Member 4 – Intelligence UI

Branch:

```text
member4-intelligence-ui
```

Responsibilities:

- Waste details
- Waste fingerprint visualization
- Root-cause explanation
- Waste Replay
- Savings
- Optimization/What-if
- Recommendations

Main folders:

```text
frontend/
```

---

### Member 5 – Backend + ML Integration

Branch:

```text
member5-backend-ml
```

Responsibilities:

- FastAPI application
- REST API endpoints
- ML service integration
- Request/response validation
- Waste analysis API
- ML pipeline connection
- Backend API documentation

Main folders:

```text
backend/api/
backend/services/ml_service.py
backend/main.py
```

---

### Member 6 – Backend + Database Integration

Branch:

```text
member6-backend-db
```

Responsibilities:

- Backend database connection
- SQLAlchemy/database integration
- Repository implementation
- Analytics queries
- Database-to-API integration
- Monitoring data services

Main folders:

```text
backend/db/
backend/services/analytics_service.py
backend/services/monitoring_service.py
```

---

## 10. Branch Rules

The following branches are used:

```text
main
member1-ml
member2-database
member3-monitoring-ui
member4-intelligence-ui
member5-backend-ml
member6-backend-db
```

Rules:

1. Do not directly develop on `main`.
2. Each member works on their assigned branch.
3. Pull the latest `main` before starting major work.
4. Commit changes regularly.
5. Push changes to the assigned branch.
6. Use Pull Requests for integration.
7. Do not overwrite another member's work.
8. Do not commit passwords, API keys, tokens, or `.env` files.
9. Do not commit large raw datasets.
10. Do not change shared interfaces without team discussion.

---

## 11. Shared Data Contract

Common resource names:

```text
machine_id
timestamp
active_tasks
workload_type
priority
workload_duration
cpu_capacity
memory_capacity
actual_cpu
actual_memory
actual_power
expected_cpu
expected_memory
expected_power
waste_score
severity
waste_type
confidence
persistent
```

---

## 12. Integration Rule

Components must communicate through the defined interfaces.

```text
ML
 ↓
ML Result
 ↓
Backend Services
 ↓
REST API
 ↓
Frontend
```

Database communication:

```text
Backend
 ↓
Repositories
 ↓
PostgreSQL
```

Frontend must never directly connect to PostgreSQL.

---

## 13. Pull Request Rule

Every completed feature should be pushed to the member's branch and integrated through a Pull Request.

Recommended format:

```text
feat: add expected resource prediction
feat: add machine monitoring dashboard
feat: add waste database models
feat: integrate ML analysis API
fix: correct waste score calculation
```

Before merging:

- Code should run successfully.
- No secrets should be committed.
- Shared interfaces must remain compatible.
- Related tests should pass.
- Conflicts must be resolved before merging.

---

## 14. Final Integration

Final integration flow:

```text
member1-ml
       \
member2-database
        \
member3-monitoring-ui
         \
member4-intelligence-ui
          \
member5-backend-ml
           \
member6-backend-db
             ↓
           Pull Requests
             ↓
            main
```

Only tested and compatible changes should be merged into `main`.
```