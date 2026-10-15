from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


MachineStatus = Literal["active", "inactive", "maintenance"]


class MachineCreate(BaseModel):
    machine_name: str = Field(min_length=1, max_length=100)
    cpu_capacity: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    memory_capacity: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    status: MachineStatus = "active"


class MachineUpdate(BaseModel):
    machine_name: str | None = Field(default=None, min_length=1, max_length=100)
    cpu_capacity: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    memory_capacity: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    status: MachineStatus | None = None


class MachineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    machine_id: int
    machine_name: str
    cpu_capacity: Decimal
    memory_capacity: Decimal
    status: MachineStatus
    created_at: datetime
