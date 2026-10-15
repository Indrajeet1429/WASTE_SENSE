from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MeasurementCreate(BaseModel):
    machine_id: int = Field(gt=0)
    workload_id: int = Field(gt=0)
    timestamp: datetime

    actual_cpu: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    actual_memory: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    actual_power: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )


class MeasurementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    measurement_id: int
    machine_id: int
    workload_id: int
    timestamp: datetime
    actual_cpu: Decimal
    actual_memory: Decimal
    actual_power: Decimal