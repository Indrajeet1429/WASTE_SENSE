from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


WasteSeverity = Literal["low", "medium", "high", "critical"]


class WasteEventCreate(BaseModel):
    machine_id: int = Field(gt=0)
    workload_id: int = Field(gt=0)

    timestamp: datetime

    waste_score: Decimal = Field(
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
    )

    severity: WasteSeverity
    waste_type: str = Field(min_length=1, max_length=100)

    confidence: Decimal = Field(
        ge=0,
        le=1,
        max_digits=5,
        decimal_places=4,
    )

    persistent: bool = False


class WasteEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    waste_id: int
    machine_id: int
    workload_id: int
    timestamp: datetime
    waste_score: Decimal
    severity: WasteSeverity
    waste_type: str
    confidence: Decimal
    persistent: bool