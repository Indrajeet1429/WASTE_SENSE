from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RecommendationCreate(BaseModel):
    waste_id: int = Field(gt=0)

    recommendation: str = Field(
        min_length=1,
        max_length=1000,
    )

    resource: str = Field(
        min_length=1,
        max_length=50,
    )

    current_value: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    suggested_value: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    estimated_benefit: Decimal = Field(
        ge=0,
        max_digits=14,
        decimal_places=2,
    )


class RecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendation_id: int
    waste_id: int
    recommendation: str
    resource: str
    current_value: Decimal
    suggested_value: Decimal
    estimated_benefit: Decimal
    created_at: datetime