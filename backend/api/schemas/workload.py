from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

WorkloadPriority = Literal["low", "normal", "high", "critical"]


class WorkloadCreate(BaseModel):
    machine_id: int = Field(gt=0)
    workload_type: str = Field(min_length=1, max_length=100)
    priority: WorkloadPriority = "normal"
    start_time: datetime
    end_time: datetime | None = None
    active_tasks: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_times(self) -> "WorkloadCreate":
        if self.end_time is not None and self.end_time < self.start_time:
            raise ValueError("end_time cannot be earlier than start_time.")
        return self


class WorkloadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    workload_id: int
    machine_id: int
    workload_type: str
    priority: WorkloadPriority
    start_time: datetime
    end_time: datetime | None
    active_tasks: int
