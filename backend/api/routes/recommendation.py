from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.api.schemas.recommendation import (
    RecommendationCreate,
    RecommendationRead,
)
from backend.db.dependencies import get_db
from database.models import Recommendation, WasteEvent


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


@router.post(
    "",
    response_model=RecommendationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_recommendation(
    payload: RecommendationCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Recommendation:
    try:
        waste_event = db.get(WasteEvent, payload.waste_id)

        if waste_event is None:
            raise HTTPException(
                status_code=404,
                detail="Waste event not found.",
            )

        recommendation = Recommendation(**payload.model_dump())

        db.add(recommendation)
        db.commit()
        db.refresh(recommendation)

        return recommendation

    except HTTPException:
        db.rollback()
        raise

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Recommendation violates a database constraint.",
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create recommendation.",
        ) from exc


@router.get(
    "",
    response_model=list[RecommendationRead],
)
def list_recommendations(
    db: Annotated[Session, Depends(get_db)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    waste_id: Annotated[int | None, Query(gt=0)] = None,
    resource: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
) -> list[Recommendation]:
    statement = (
        select(Recommendation)
        .order_by(
            Recommendation.created_at.desc(),
            Recommendation.recommendation_id.desc(),
        )
        .offset(offset)
        .limit(limit)
    )

    if waste_id is not None:
        statement = statement.where(
            Recommendation.waste_id == waste_id
        )

    if resource is not None:
        statement = statement.where(
            Recommendation.resource == resource
        )

    try:
        return list(db.scalars(statement).all())

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve recommendations.",
        ) from exc


@router.get(
    "/{recommendation_id}",
    response_model=RecommendationRead,
)
def get_recommendation(
    recommendation_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Recommendation:
    try:
        recommendation = db.get(
            Recommendation,
            recommendation_id,
        )

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve recommendation.",
        ) from exc

    if recommendation is None:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found.",
        )

    return recommendation