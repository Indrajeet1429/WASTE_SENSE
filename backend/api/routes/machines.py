from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.api.schemas.machine import MachineCreate, MachineRead, MachineUpdate
from backend.db.dependencies import get_db
from database.models import Machine

router = APIRouter(prefix="/machines", tags=["Machines"])


@router.post(
    "",
    response_model=MachineRead,
    status_code=status.HTTP_201_CREATED,
)
def create_machine(
    payload: MachineCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Machine:
    machine = Machine(**payload.model_dump())
    db.add(machine)

    try:
        db.commit()
        db.refresh(machine)
        return machine
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A machine with this name may already exist, or the data violates a database constraint.",
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create machine.",
        ) from exc


@router.get("", response_model=list[MachineRead])
def list_machines(
    db: Annotated[Session, Depends(get_db)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    machine_status: Annotated[
        str | None,
        Query(alias="status", pattern="^(active|inactive|maintenance)$"),
    ] = None,
) -> list[Machine]:
    statement = select(Machine).order_by(Machine.machine_id).offset(offset).limit(limit)

    if machine_status is not None:
        statement = statement.where(Machine.status == machine_status)

    try:
        return list(db.scalars(statement).all())
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve machines.",
        ) from exc


@router.get("/{machine_id}", response_model=MachineRead)
def get_machine(
    machine_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Machine:
    machine = db.get(Machine, machine_id)

    if machine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found.",
        )

    return machine


@router.patch("/{machine_id}", response_model=MachineRead)
def update_machine(
    machine_id: int,
    payload: MachineUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> Machine:
    machine = db.get(Machine, machine_id)

    if machine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found.",
        )

    changes = payload.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide at least one field to update.",
        )

    if any(value is None for value in changes.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Updated fields cannot be null.",
        )

    for field, value in changes.items():
        setattr(machine, field, value)

    try:
        db.commit()
        db.refresh(machine)
        return machine
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The update conflicts with a database constraint.",
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update machine.",
        ) from exc


@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_machine(
    machine_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    machine = db.get(Machine, machine_id)

    if machine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found.",
        )

    try:
        db.delete(machine)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This machine is referenced by other records and cannot be deleted.",
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete machine.",
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
