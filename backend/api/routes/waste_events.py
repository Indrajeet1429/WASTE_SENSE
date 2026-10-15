from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from backend.api.schemas.waste_event import (
    WasteEventCreate,
    WasteEventRead,
    WasteSeverity,
)
from backend.db.dependencies import get_db
from database.models import Machine, WasteEvent, Workload


router = APIRouter(
    prefix="/waste-events",
    tags=["Waste Events"],
)


@router.post(
    "",
    response_model=WasteEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_waste_event(
    payload: WasteEventCreate,
    db: Annotated[Session, Depends(get_db)],
) -> WasteEvent:
    machine = db.get(Machine, payload.machine_id)

    if machine is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found.",
        )

    workload = db.get(Workload, payload.workload_id)

    if workload is None:
        raise HTTPException(
            status_code=404,
            detail="Workload not found.",
        )

    if workload.machine_id != payload.machine_id:
        raise HTTPException(
            status_code=422,
            detail="The workload does not belong to the specified machine.",
        )

    waste_event = WasteEvent(**payload.model_dump())
    db.add(waste_event)

    try:
        db.commit()
        db.refresh(waste_event)
        return waste_event

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Waste event violates a database constraint.",
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to save waste event.",
        ) from exc


@router.get(
    "",
    response_model=list[WasteEventRead],
)
def list_waste_events(
    db: Annotated[Session, Depends(get_db)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    machine_id: Annotated[int | None, Query(gt=0)] = None,
    workload_id: Annotated[int | None, Query(gt=0)] = None,
    severity: WasteSeverity | None = None,
    persistent: bool | None = None,
) -> list[WasteEvent]:
    statement = (
        select(WasteEvent)
        .order_by(WasteEvent.timestamp.desc(), WasteEvent.waste_id.desc())
        .offset(offset)
        .limit(limit)
    )

    if machine_id is not None:
        statement = statement.where(
            WasteEvent.machine_id == machine_id
        )

    if workload_id is not None:
        statement = statement.where(
            WasteEvent.workload_id == workload_id
        )

    if severity is not None:
        statement = statement.where(
            WasteEvent.severity == severity
        )

    if persistent is not None:
        statement = statement.where(
            WasteEvent.persistent == persistent
        )

    try:
        return list(db.scalars(statement).all())

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve waste events.",
        ) from exc


@router.get(
    "/{waste_id}",
    response_model=WasteEventRead,
)
def get_waste_event(
    waste_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> WasteEvent:
    try:
        waste_event = db.get(WasteEvent, waste_id)

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve waste event.",
        ) from exc

    if waste_event is None:
        raise HTTPException(
            status_code=404,
            detail="Waste event not found.",
        )

    return waste_event