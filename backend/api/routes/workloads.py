from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.api.schemas.workload import WorkloadCreate, WorkloadRead
from backend.db.dependencies import get_db
from database.models import Machine, Workload

router = APIRouter(prefix="/workloads", tags=["Workloads"])


@router.post(
    "",
    response_model=WorkloadRead,
    status_code=status.HTTP_201_CREATED,
)
def create_workload(
    payload: WorkloadCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Workload:
    machine = db.get(Machine, payload.machine_id)

    if machine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found.",
        )

    workload = Workload(**payload.model_dump())
    db.add(workload)

    try:
        db.commit()
        db.refresh(workload)
        return workload

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Workload violates a database constraint.",
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create workload.",
        ) from exc


@router.get("", response_model=list[WorkloadRead])
def list_workloads(
    db: Annotated[Session, Depends(get_db)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    machine_id: Annotated[int | None, Query(gt=0)] = None,
) -> list[Workload]:
    statement = (
        select(Workload)
        .order_by(Workload.workload_id)
        .offset(offset)
        .limit(limit)
    )

    if machine_id is not None:
        statement = statement.where(Workload.machine_id == machine_id)

    try:
        return list(db.scalars(statement).all())

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve workloads.",
        ) from exc


@router.get("/{workload_id}", response_model=WorkloadRead)
def get_workload(
    workload_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Workload:
    try:
        workload = db.get(Workload, workload_id)

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve workload.",
        ) from exc

    if workload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workload not found.",
        )

    return workload
