from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.api.schemas.alert import (
    AlertCreate,
    AlertRead,
    AlertSeverity,
    AlertStatus,
    AlertStatusUpdate,
)
from backend.db.dependencies import get_db
from database.models import Alert, WasteEvent


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


@router.post(
    "",
    response_model=AlertRead,
    status_code=status.HTTP_201_CREATED,
)
def create_alert(
    payload: AlertCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Alert:
    waste_event = db.get(WasteEvent, payload.waste_id)

    if waste_event is None:
        raise HTTPException(
            status_code=404,
            detail="Waste event not found.",
        )

    alert = Alert(
        waste_id=payload.waste_id,
        severity=payload.severity,
        message=payload.message,
        status="open",
    )

    db.add(alert)

    try:
        db.commit()
        db.refresh(alert)
        return alert

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Alert violates a database constraint.",
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create alert.",
        ) from exc


@router.get(
    "",
    response_model=list[AlertRead],
)
def list_alerts(
    db: Annotated[Session, Depends(get_db)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    waste_id: Annotated[int | None, Query(gt=0)] = None,
    severity: AlertSeverity | None = None,
    alert_status: AlertStatus | None = Query(default=None, alias="status"),
) -> list[Alert]:
    statement = (
        select(Alert)
        .order_by(Alert.created_at.desc(), Alert.alert_id.desc())
        .offset(offset)
        .limit(limit)
    )

    if waste_id is not None:
        statement = statement.where(Alert.waste_id == waste_id)

    if severity is not None:
        statement = statement.where(Alert.severity == severity)

    if alert_status is not None:
        statement = statement.where(Alert.status == alert_status)

    try:
        return list(db.scalars(statement).all())

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve alerts.",
        ) from exc


@router.get(
    "/{alert_id}",
    response_model=AlertRead,
)
def get_alert(
    alert_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Alert:
    try:
        alert = db.get(Alert, alert_id)

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve alert.",
        ) from exc

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found.",
        )

    return alert


@router.patch(
    "/{alert_id}/status",
    response_model=AlertRead,
)
def update_alert_status(
    alert_id: int,
    payload: AlertStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> Alert:
    try:
        alert = db.get(Alert, alert_id)

        if alert is None:
            raise HTTPException(
                status_code=404,
                detail="Alert not found.",
            )

        if payload.status == "resolved":
            if alert.status != "resolved":
                alert.resolved_at = datetime.now(timezone.utc)

        else:
            alert.resolved_at = None

        alert.status = payload.status

        db.commit()
        db.refresh(alert)

        return alert

    except HTTPException:
        db.rollback()
        raise

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Alert status conflicts with a database constraint.",
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to update alert status.",
        ) from exc