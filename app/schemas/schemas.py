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


class CompetencySpecialtyItem(BaseModel):
    specialty: str
    leadership: int | None = None
    analysis: int | None = None
    partnership: int | None = None
    digital_literacy: int | None = None
    critical_thinking: int | None = None
    creativity: int | None = None
    communication: int | None = None
    teamwork: int | None = None
    emotional_intelligence: int | None = None
    adaptability: int | None = None
    self_education: int | None = None
    responsibility: int | None = None


class CompetencyBySpecialtiesResponse(BaseModel):
    data: list[CompetencySpecialtyItem]


class MotivatorSpecialtyItem(BaseModel):
    specialty: str
    career: int | None = None
    altruism: int | None = None
    creativity: int | None = None
    money: int | None = None
    power: int | None = None
    independence: int | None = None
    knowledge: int | None = None
    communication: int | None = None
    recognition: int | None = None
    safety: int | None = None
    achievement: int | None = None
    self_development: int | None = None
    leadership: int | None = None
    teamwork: int | None = None
    stability: int | None = None
    challenge: int | None = None


class MotivatorBySpecialtiesResponse(BaseModel):
    data: list[MotivatorSpecialtyItem]
