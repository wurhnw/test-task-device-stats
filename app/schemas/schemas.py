from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime


class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    user_id: UUID | None = None


class DeviceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    user_id: UUID | None
    created_at: datetime


class ReadingCreate(BaseModel):
    x: float
    y: float
    z: float


class ReadingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: UUID
    x: float
    y: float
    z: float
    created_at: datetime


class AxisStats(BaseModel):
    min: float | None = None
    max: float | None = None
    count: int = 0
    sum: float = 0.0
    median: float | None = None


class StatsResponse(BaseModel):
    device_id: UUID | None = None
    period_from: datetime | None = None
    period_to: datetime | None = None
    x: AxisStats
    y: AxisStats
    z: AxisStats


class UserStatsResponse(BaseModel):
    user_id: UUID
    period_from: datetime | None = None
    period_to: datetime | None = None
    aggregated: StatsResponse
    per_device: list[StatsResponse]


class TaskAccepted(BaseModel):
    task_id: str
    status: str = "PENDING"


class TaskResult(BaseModel):
    task_id: str
    status: str
    result: dict | None = None
