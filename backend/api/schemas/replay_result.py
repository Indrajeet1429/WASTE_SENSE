from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ReplayResultCreate(BaseModel):
    waste_id: int = Field(gt=0)

    actual_cpu: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    expected_cpu: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    actual_power: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    expected_power: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    estimated_saving: Decimal = Field(
        ge=0,
        max_digits=14,
        decimal_places=2,
    )


class ReplayResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    replay_id: int
    waste_id: int
    actual_cpu: Decimal
    expected_cpu: Decimal
    actual_power: Decimal
    expected_power: Decimal
    estimated_saving: Decimal
    created_at: datetime