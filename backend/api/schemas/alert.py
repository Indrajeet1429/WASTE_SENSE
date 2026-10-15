from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


AlertSeverity = Literal["low", "medium", "high", "critical"]
AlertStatus = Literal["open", "acknowledged", "resolved"]


class AlertCreate(BaseModel):
    waste_id: int = Field(gt=0)
    severity: AlertSeverity
    message: str = Field(min_length=1, max_length=500)


class AlertStatusUpdate(BaseModel):
    status: AlertStatus


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    alert_id: int
    waste_id: int
    severity: AlertSeverity
    message: str
    status: AlertStatus
    created_at: datetime
    resolved_at: datetime | None