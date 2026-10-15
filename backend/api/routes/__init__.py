"""Versioned API routes connecting the frontend to persistence and ML."""
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ValidationError
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.db.dependencies import get_db
from backend.api.schemas.machine import MachineCreate, MachineRead, MachineUpdate
from backend.api.schemas.workload import WorkloadCreate, WorkloadRead
from backend.api.schemas.measurement import MeasurementCreate, MeasurementRead
from backend.api.schemas.waste_event import WasteEventCreate, WasteEventRead
from backend.api.schemas.alert import AlertCreate, AlertRead, AlertStatusUpdate
from backend.api.schemas.saving import SavingCreate, SavingRead
from backend.api.schemas.replay_result import ReplayResultCreate, ReplayResultRead
from backend.api.schemas.recommendation import RecommendationCreate, RecommendationRead
from backend.services.ml_service import (
    MLInputError, MLModelUnavailableError, MLServiceError, analyze_workload,
)
from database.models import (
    Alert, Machine, Recommendation, ReplayResult, ResourceMeasurement,
    Saving, WasteEvent, Workload,
)

router = APIRouter(prefix="/api/v1", tags=["WASTESENSE API"])

class AnalyzeRequest(BaseModel):
    machine_id: str
    timestamp: str
    active_tasks: int
    workload_type: str = "COMPUTE"
    priority: float = 1.0
    workload_duration: float = 0.0
    cpu_capacity: float
    memory_capacity: float
    actual_cpu: float
    actual_memory: float
    # Additional engineered features can be passed by advanced clients.
    avg_priority: float | None = None
    max_priority: float | None = None
    elapsed_minutes: float | None = None
    trace_hour: float | None = None
    day_of_trace: float | None = None
    is_peak_period: float | None = None


def _dump(row: Any) -> dict[str, Any]:
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def _jsonable(row: Any) -> dict[str, Any]:
    from fastapi.encoders import jsonable_encoder
    return jsonable_encoder(_dump(row))

RESOURCE_SPECS = {
    "machines": (Machine, MachineCreate, MachineRead, MachineUpdate, "machine_id"),
    "workloads": (Workload, WorkloadCreate, WorkloadRead, None, "workload_id"),
    "measurements": (ResourceMeasurement, MeasurementCreate, MeasurementRead, None, "measurement_id"),
    "waste-events": (WasteEvent, WasteEventCreate, WasteEventRead, None, "waste_id"),
    "alerts": (Alert, AlertCreate, AlertRead, None, "alert_id"),
    "savings": (Saving, SavingCreate, SavingRead, None, "saving_id"),
    "replay-results": (ReplayResult, ReplayResultCreate, ReplayResultRead, None, "replay_id"),
    "recommendations": (Recommendation, RecommendationCreate, RecommendationRead, None, "recommendation_id"),
}

# Register consistent list/get/create/update/delete endpoints for each frontend resource.
def _register_resource(slug: str, spec: tuple) -> None:
    model, create_schema, read_schema, update_schema, id_field = spec

    def list_rows(offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db), **_unused):
        query = db.query(model)
        # Apply supported filters passed by the frontend (machine_id, waste_id, status, severity).
        # Request-level filtering is handled by a dedicated endpoint below for common fields.
        return [_jsonable(row) for row in query.order_by(getattr(model, id_field).desc()).offset(offset).limit(limit).all()]

    async def list_endpoint(offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), machine_id: int | None = None, workload_id: int | None = None, waste_id: int | None = None, status_filter: str | None = Query(None, alias="status"), severity: str | None = None, db: Session = Depends(get_db)):
        query = db.query(model)
        for key, value in (("machine_id", machine_id), ("workload_id", workload_id), ("waste_id", waste_id), ("status", status_filter), ("severity", severity)):
            if value is not None and hasattr(model, key):
                query = query.filter(getattr(model, key) == value)
        return [_jsonable(row) for row in query.order_by(getattr(model, id_field).desc()).offset(offset).limit(limit).all()]

    async def get_endpoint(item_id: int, db: Session = Depends(get_db)):
        row = db.get(model, item_id)
        if row is None:
            raise HTTPException(status_code=404, detail=f"{slug} record {item_id} not found")
        return _jsonable(row)

    async def create_endpoint(payload: dict[str, Any], db: Session = Depends(get_db)):
        try:
            parsed = create_schema.model_validate(payload)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=jsonable_encoder(exc.errors())) from exc
        row = model(**parsed.model_dump())
        db.add(row)
        try:
            db.commit()
            db.refresh(row)
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail="Record conflicts with existing data or a referenced record does not exist.") from exc
        return _jsonable(row)

    async def update_endpoint(item_id: int, payload: dict[str, Any], db: Session = Depends(get_db)):
        row = db.get(model, item_id)
        if row is None:
            raise HTTPException(status_code=404, detail=f"{slug} record {item_id} not found")
        if slug == "alerts" and "status" in payload:
            try:
                patch = AlertStatusUpdate.model_validate(payload).model_dump(exclude_unset=True)
            except ValidationError as exc:
                raise HTTPException(status_code=422, detail=jsonable_encoder(exc.errors())) from exc
            row.status = patch["status"]
            row.resolved_at = datetime.now(timezone.utc) if row.status == "resolved" else None
        elif update_schema is not None:
            try:
                patch = update_schema.model_validate(payload).model_dump(exclude_unset=True, exclude_none=True)
            except ValidationError as exc:
                raise HTTPException(status_code=422, detail=jsonable_encoder(exc.errors())) from exc
            for key, value in patch.items():
                setattr(row, key, value)
        else:
            allowed = {c.name for c in model.__table__.columns} - {id_field, "created_at", "estimated_at"}
            for key, value in payload.items():
                if key in allowed:
                    setattr(row, key, value)
        try:
            db.commit(); db.refresh(row)
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail="Update conflicts with database constraints.") from exc
        return _jsonable(row)

    async def delete_endpoint(item_id: int, db: Session = Depends(get_db)):
        row = db.get(model, item_id)
        if row is None:
            raise HTTPException(status_code=404, detail=f"{slug} record {item_id} not found")
        db.delete(row)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail="Record is referenced by other records and cannot be deleted.") from exc
        return {"deleted": True, "id": item_id}

    router.add_api_route(f"/{slug}", list_endpoint, methods=["GET"], name=f"list_{slug}")
    router.add_api_route(f"/{slug}", create_endpoint, methods=["POST"], status_code=status.HTTP_201_CREATED, name=f"create_{slug}")
    router.add_api_route(f"/{slug}/{{item_id}}", get_endpoint, methods=["GET"], name=f"get_{slug}")
    router.add_api_route(f"/{slug}/{{item_id}}", update_endpoint, methods=["PATCH"], name=f"update_{slug}")
    router.add_api_route(f"/{slug}/{{item_id}}", delete_endpoint, methods=["DELETE"], name=f"delete_{slug}")

for _slug, _spec in RESOURCE_SPECS.items():
    _register_resource(_slug, _spec)

@router.get("/health")
def health():
    return {"status": "healthy", "service": "wastesense-backend"}

@router.get("/health/database")
def database_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database connection failed") from exc

@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    machines = db.query(Machine).count()
    active = db.query(Machine).filter(Machine.status == "active").count()
    workloads = db.query(Workload).filter(Workload.end_time.is_(None)).count()
    waste = db.query(WasteEvent).count()
    alerts = db.query(Alert).filter(Alert.status == "open").count()
    savings = db.query(func.coalesce(func.sum(Saving.cost_saving), 0)).scalar() or 0
    return {"total_machines": machines, "active_machines": active, "active_workloads": workloads, "waste_events": waste, "open_alerts": alerts, "potential_savings": float(savings)}

@router.get("/trends")
def trends(db: Session = Depends(get_db)):
    rows = db.query(ResourceMeasurement).order_by(ResourceMeasurement.timestamp.asc()).limit(500).all()
    return [_jsonable(row) for row in rows]

@router.post("/waste/analyze")
def analyze(request: AnalyzeRequest):
    payload = request.model_dump()
    try:
        # Bridge API-friendly workload input to the exact feature names used by trained models.
        timestamp = datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
        priority = float(payload.get("priority", 1.0))
        payload.update({
            "avg_priority": payload.get("avg_priority") if payload.get("avg_priority") is not None else priority,
            "max_priority": payload.get("max_priority") if payload.get("max_priority") is not None else priority,
            "elapsed_minutes": payload.get("elapsed_minutes") if payload.get("elapsed_minutes") is not None else float(payload.get("workload_duration", 0.0)),
            "trace_hour": payload.get("trace_hour") if payload.get("trace_hour") is not None else timestamp.hour,
            "day_of_trace": payload.get("day_of_trace") if payload.get("day_of_trace") is not None else timestamp.timetuple().tm_yday,
            "is_peak_period": payload.get("is_peak_period") if payload.get("is_peak_period") is not None else int(9 <= timestamp.hour <= 17),
        })
        return analyze_workload(payload)
    except (ValueError, TypeError, MLInputError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except MLModelUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except MLServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("/optimization")
def optimization(db: Session = Depends(get_db)):
    rows = db.query(Recommendation).order_by(Recommendation.created_at.desc()).limit(100).all()
    return [_jsonable(row) for row in rows]

@router.patch("/alerts/{alert_id}/status")
def update_alert_status(alert_id: int, payload: AlertStatusUpdate, db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = payload.status
    alert.resolved_at = datetime.now(timezone.utc) if payload.status == "resolved" else None
    db.commit()
    db.refresh(alert)
    return _jsonable(alert)
