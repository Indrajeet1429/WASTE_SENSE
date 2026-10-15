from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.api.schemas.replay_result import (
    ReplayResultCreate,
    ReplayResultRead,
)
from backend.db.dependencies import get_db
from database.models import ReplayResult, WasteEvent


router = APIRouter(
    prefix="/replay-results",
    tags=["Replay Results"],
)


@router.post(
    "",
    response_model=ReplayResultRead,
    status_code=status.HTTP_201_CREATED,
)
def create_replay_result(
    payload: ReplayResultCreate,
    db: Annotated[Session, Depends(get_db)],
) -> ReplayResult:
    try:
        waste_event = db.get(WasteEvent, payload.waste_id)

        if waste_event is None:
            raise HTTPException(
                status_code=404,
                detail="Waste event not found.",
            )

        existing_result = db.scalar(
            select(ReplayResult).where(
                ReplayResult.waste_id == payload.waste_id
            )
        )

        if existing_result is not None:
            raise HTTPException(
                status_code=409,
                detail="A replay result already exists for this waste event.",
            )

        replay_result = ReplayResult(**payload.model_dump())
        db.add(replay_result)
        db.commit()
        db.refresh(replay_result)

        return replay_result

    except HTTPException:
        db.rollback()
        raise

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Replay result violates a database constraint.",
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to save replay result.",
        ) from exc


@router.get(
    "",
    response_model=list[ReplayResultRead],
)
def list_replay_results(
    db: Annotated[Session, Depends(get_db)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    waste_id: Annotated[int | None, Query(gt=0)] = None,
) -> list[ReplayResult]:
    statement = (
        select(ReplayResult)
        .order_by(
            ReplayResult.created_at.desc(),
            ReplayResult.replay_id.desc(),
        )
        .offset(offset)
        .limit(limit)
    )

    if waste_id is not None:
        statement = statement.where(
            ReplayResult.waste_id == waste_id
        )

    try:
        return list(db.scalars(statement).all())

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve replay results.",
        ) from exc


@router.get(
    "/{replay_id}",
    response_model=ReplayResultRead,
)
def get_replay_result(
    replay_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> ReplayResult:
    try:
        replay_result = db.get(ReplayResult, replay_id)

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve replay result.",
        ) from exc

    if replay_result is None:
        raise HTTPException(
            status_code=404,
            detail="Replay result not found.",
        )

    return replay_result