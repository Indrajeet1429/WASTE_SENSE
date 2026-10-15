from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.api.schemas.saving import SavingCreate, SavingRead
from backend.db.dependencies import get_db
from database.models import Saving, WasteEvent


router = APIRouter(
    prefix="/savings",
    tags=["Savings"],
)


@router.post(
    "",
    response_model=SavingRead,
    status_code=status.HTTP_201_CREATED,
)
def create_saving(
    payload: SavingCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Saving:
    try:
        waste_event = db.get(WasteEvent, payload.waste_id)

        if waste_event is None:
            raise HTTPException(
                status_code=404,
                detail="Waste event not found.",
            )

        existing_saving = db.scalar(
            select(Saving).where(
                Saving.waste_id == payload.waste_id
            )
        )

        if existing_saving is not None:
            raise HTTPException(
                status_code=409,
                detail="A savings record already exists for this waste event.",
            )

        saving = Saving(**payload.model_dump())
        db.add(saving)
        db.commit()
        db.refresh(saving)

        return saving

    except HTTPException:
        db.rollback()
        raise

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Savings record conflicts with a database constraint.",
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create savings record.",
        ) from exc


@router.get(
    "",
    response_model=list[SavingRead],
)
def list_savings(
    db: Annotated[Session, Depends(get_db)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    waste_id: Annotated[int | None, Query(gt=0)] = None,
) -> list[Saving]:
    statement = (
        select(Saving)
        .order_by(Saving.estimated_at.desc(), Saving.saving_id.desc())
        .offset(offset)
        .limit(limit)
    )

    if waste_id is not None:
        statement = statement.where(
            Saving.waste_id == waste_id
        )

    try:
        return list(db.scalars(statement).all())

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve savings records.",
        ) from exc


@router.get(
    "/{saving_id}",
    response_model=SavingRead,
)
def get_saving(
    saving_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Saving:
    try:
        saving = db.get(Saving, saving_id)

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve savings record.",
        ) from exc

    if saving is None:
        raise HTTPException(
            status_code=404,
            detail="Savings record not found.",
        )

    return saving