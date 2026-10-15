# WASTESENSE 2.0 — Local Windows Run Guide

## What this repair connects
- React/Vite frontend uses the `/api/v1` FastAPI endpoints (mock mode is disabled).
- FastAPI exposes CRUD endpoints for machines, workloads, measurements, waste events, alerts, savings, replay results, and recommendations.
- SQLAlchemy persists data. If `DATABASE_URL` is not set, the app uses a local SQLite file named `wastesense.db` so it can start without a PostgreSQL setup. PostgreSQL can be selected using `.env`.
- On first start, the local database is created and a small demo dataset is seeded if it is empty.
- The `/api/v1/waste/analyze` endpoint calls the saved CatBoost inference pipeline.

## Prerequisites
- Python 3.12 recommended for broad ML-package compatibility.
- Node.js LTS and npm.
- If using PostgreSQL instead of the default SQLite demo database, PostgreSQL must be running and a database/user must exist.

## 1. Start the backend
Open a terminal in the folder containing `backend/`, `database/`, `ml/`, and `frontend/`.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

If PowerShell blocks activation, run the environment's Python directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Check these URLs:
- API health: http://127.0.0.1:8000/api/v1/health
- Database health: http://127.0.0.1:8000/api/v1/health/database
- Swagger docs: http://127.0.0.1:8000/docs

## 2. Start the frontend in a second terminal
```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```
Open the local URL printed by Vite, usually http://localhost:5173.

The `frontend/.env` file sets `VITE_USE_MOCK=false` and proxies `/api` to `http://127.0.0.1:8000`.

## 3. Open the dashboard
The app uses browser-local signup/login. Open `/signup`, create a local demo account, and then open the dashboard. This is frontend-only demo authentication; it is not production authentication.

## 4. Database selection
Default: SQLite local demo DB. To use PostgreSQL, create a root `.env` file and set:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/wastesense
DATABASE_PASSWORD=YOUR_PASSWORD
```

Replace the placeholder with your own local credentials. Never commit `.env` or real credentials.

## Important limitations
- Seeded records are demo data, not live telemetry from Google/Alibaba traces.
- CPU/memory model evaluation documents weak predictive performance; inference success does not imply high accuracy. Do not present the demo's waste scores/savings as guaranteed real-world savings.
- The saved power model works at aggregated PDU-time level and requires its full PDU feature payload; it is not a per-machine watt meter.
- The app should be considered locally integrated for development/demo use, not production-hardened (authentication, authorization, telemetry ingestion, and deployment hardening remain separate work).
