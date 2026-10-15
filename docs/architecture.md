### Next step — create `docs/architecture.md`

```markdown id="x0t4cf"
# WASTESENSE Architecture

## System Architecture

WASTESENSE uses a single-server architecture.

```text
                    WASTESENSE
                         |
              +----------+----------+
              |                     |
          Frontend                NGINX
           React                    |
              |                     |
              +---------> FastAPI <+
                            |
                +-----------+-----------+
                |                       |
             ML Layer              PostgreSQL
                |
       Expected Resource Model
                |
        Anomaly Detection
                |
          Waste Intelligence
                |
       Score / Fingerprint
                |
        Root Cause / Replay
                |
       Savings / Recommendation
```

## Main Components

### Frontend

React-based interface responsible for:

- Monitoring dashboard
- Machine details
- Waste events
- Waste trends
- Alerts
- Waste replay
- Optimization
- Savings

### Backend

FastAPI provides REST APIs under `/api`.

Responsibilities:

- API requests
- Authentication and configuration
- ML integration
- Database integration
- Waste analysis
- Analytics

### ML Layer

The ML layer performs:

1. Expected resource prediction
2. Actual vs expected comparison
3. Residual analysis
4. Anomaly detection
5. Waste scoring
6. Waste fingerprinting
7. Root-cause analysis
8. Waste replay
9. Savings estimation
10. Optimization recommendations

### PostgreSQL

Stores:

- Machines
- Workloads
- Resource measurements
- Waste events
- Alerts
- Trends
- Savings estimates
- Replay results
- Recommendations

## Data Flow

```text
Workload Data
      |
      v
Feature Engineering
      |
      v
Expected Resource Prediction
      |
      v
Actual vs Expected
      |
      v
Residual Analysis
      |
      v
Anomaly Detection
      |
      v
Waste Intelligence
      |
      +----> Waste Score
      |
      +----> Waste Fingerprint
      |
      +----> Root Cause
      |
      +----> Waste Replay
      |
      +----> Savings
      |
      +----> Recommendation
      |
      v
PostgreSQL
      |
      v
FastAPI
      |
      v
React Dashboard
```

## Team Integration

Each member works on an assigned branch.

```text
member1-ml
member2-database
member3-monitoring-ui
member4-intelligence-ui
member5-backend-ml
member6-backend-db
        |
        v
    Pull Request
        |
        v
       main
```

Only tested and compatible changes should be merged into `main`.
```