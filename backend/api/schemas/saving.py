from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SavingCreate(BaseModel):
    waste_id: int = Field(gt=0)

    cpu_saving: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    memory_saving: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    power_saving: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    cost_saving: Decimal = Field(
        ge=0,
        max_digits=14,
        decimal_places=2,
    )


class SavingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    saving_id: int
    waste_id: int
    cpu_saving: Decimal
    memory_saving: Decimal
    power_saving: Decimal
    cost_saving: Decimal
    estimated_at: datetime