from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.api.schemas.measurement import (
    MeasurementCreate,
    MeasurementRead,
)
from backend.db.dependencies import get_db
from database.models import Machine, ResourceMeasurement, Workload


router = APIRouter(
    prefix="/measurements",
    tags=["Resource Measurements"],
)


@router.post(
    "",
    response_model=MeasurementRead,
    status_code=status.HTTP_201_CREATED,
)
def create_measurement(
    payload: MeasurementCreate,
    db: Annotated[Session, Depends(get_db)],
) -> ResourceMeasurement:

    machine = db.get(Machine, payload.machine_id)

    if machine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found.",
        )

    workload = db.get(Workload, payload.workload_id)

    if workload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workload not found.",
        )

    if workload.machine_id != payload.machine_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The workload does not belong to the specified machine.",
        )

    measurement = ResourceMeasurement(**payload.model_dump())
    db.add(measurement)

    try:
        db.commit()
        db.refresh(measurement)
        return measurement

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Measurement conflicts with a database constraint. "
                "A measurement may already exist for this machine, "
                "workload, and timestamp."
            ),
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save resource measurement.",
        ) from exc


@router.get("", response_model=list[MeasurementRead])
def list_measurements(
    db: Annotated[Session, Depends(get_db)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    machine_id: Annotated[int | None, Query(gt=0)] = None,
    workload_id: Annotated[int | None, Query(gt=0)] = None,
) -> list[ResourceMeasurement]:

    statement = (
        select(ResourceMeasurement)
        .order_by(ResourceMeasurement.measurement_id)
        .offset(offset)
        .limit(limit)
    )

    if machine_id is not None:
        statement = statement.where(
            ResourceMeasurement.machine_id == machine_id
        )

    if workload_id is not None:
        statement = statement.where(
            ResourceMeasurement.workload_id == workload_id
        )

    try:
        return list(db.scalars(statement).all())

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve resource measurements.",
        ) from exc


@router.get(
    "/{measurement_id}",
    response_model=MeasurementRead,
)
def get_measurement(
    measurement_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> ResourceMeasurement:

    try:
        measurement = db.get(
            ResourceMeasurement,
            measurement_id,
        )

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve resource measurement.",
        ) from exc

    if measurement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource measurement not found.",
        )

    return measurement