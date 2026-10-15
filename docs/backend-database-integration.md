# WASTESENSE Backend and Database Integration

## 1. Overview

WASTESENSE uses FastAPI to expose REST API endpoints and PostgreSQL to store application data. SQLAlchemy provides database access, and Alembic manages database schema migrations.

The backend currently supports machines, workloads, resource measurements, waste events, alerts, savings, replay results, and recommendations.

## 2. Technology Stack

* Python 3.12
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Pydantic
* Uvicorn
* Pytest
* HTTPX for API testing

## 3. Prerequisites

Install the following before setting up the project:

* Python 3.12
* PostgreSQL
* Git

## 4. Local Setup

Open PowerShell in the repository root.

### Create a virtual environment

If the project virtual environment does not already exist, run:

```powershell
py -3.12 -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Configure environment variables

Create a local environment file:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and provide the correct local PostgreSQL credentials.

Never commit `.env` or publish database credentials.

### Environment variables

| Variable            | Purpose                                 |
| ------------------- | --------------------------------------- |
| `APP_NAME`          | Application name                        |
| `APP_VERSION`       | Application version                     |
| `DATABASE_URL`      | SQLAlchemy PostgreSQL connection URL    |
| `DATABASE_PASSWORD` | PostgreSQL password supplied separately |

The example configuration assumes PostgreSQL is running on `localhost:5432` and the database is named `wastesense`.

Adjust the connection settings if your environment differs.

## 5. Database Migrations

The Alembic configuration is located at `database/alembic.ini`.

### Check the current migration revision

```powershell
.\.venv\Scripts\python.exe -m alembic -c database\alembic.ini current
```

### Apply pending migrations

```powershell
.\.venv\Scripts\python.exe -m alembic -c database\alembic.ini upgrade head
```

The database schema includes tables for:

* Machines
* Workloads
* Resource measurements
* Waste events
* Alerts
* Savings
* Replay results
* Recommendations

The `alembic_version` table tracks the applied migration revision.

## 6. Start the API

Run the following command from the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

The local API server should be available at:

`http://127.0.0.1:8000`

### Useful endpoints

| Endpoint                  | Purpose                           |
| ------------------------- | --------------------------------- |
| `/api/v1/health`          | Application health                |
| `/api/v1/health/database` | Database connectivity health      |
| `/docs`                   | Interactive Swagger documentation |
| `/openapi.json`           | OpenAPI specification             |

## 7. API Capabilities

All API routes use the `/api/v1` prefix.

| Resource              | Supported operations                              |
| --------------------- | ------------------------------------------------- |
| Machines              | Create, list, retrieve, update                    |
| Workloads             | Create, list, retrieve                            |
| Resource measurements | Create, list, retrieve                            |
| Waste events          | Create, list, retrieve, filter                    |
| Alerts                | Create, list, retrieve, update status             |
| Savings               | Create, list, retrieve, prevent duplicate records |
| Replay results        | Create, list, retrieve, prevent duplicate records |
| Recommendations       | Create, list, retrieve                            |

Refer to `/docs` for the registered endpoints, request schemas, response schemas, and status codes.

## 8. Validation and Data Integrity

The API uses Pydantic schemas to validate incoming requests.

The database enforces foreign-key relationships and relevant constraints.

Waste-event validation includes:

* Waste score between 0 and 100.
* Confidence between 0 and 1.
* Severity restricted to `low`, `medium`, `high`, or `critical`.
* Valid machine and workload references.
* Workload ownership matching the specified machine.

Alert status transitions and duplicate protection for savings and replay results are covered by the existing integration tests.

## 9. Run Tests

Run the complete test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Check dependency consistency:

```powershell
.\.venv\Scripts\python.exe -m pip check
```

The latest recorded test run completed with 16 passing tests. Run the suite again after code changes to verify the current state.

## 10. ML Integration Status

The backend supports creating and retrieving waste-event records.

The actual ML model and its inference integration are not included in this backend milestone. Integration depends on the ML model and prediction interface being supplied by the responsible team member.

A manually submitted waste event must not be represented as an actual ML prediction.

## 11. Security and Operational Notes

* Never commit `.env` or real credentials.
* Keep `.env.example` limited to placeholder configuration.
* Do not expose PostgreSQL publicly without appropriate security controls.
* Use appropriate credentials for each deployment environment.
* Keep database transactions and error handling consistent across routes.
* Review debug settings and logging configuration before deployment.
