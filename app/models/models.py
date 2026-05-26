from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    devices: Mapped[list["Device"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User | None] = relationship(back_populates="devices")
    readings: Mapped[list["Reading"]] = relationship(back_populates="device", cascade="all, delete-orphan")


class CompetencyProfile(Base):
    __tablename__ = "competency_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    specialty: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    year: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    course: Mapped[str | None] = mapped_column(String(10), nullable=True)
    leadership: Mapped[float | None] = mapped_column(Float, nullable=True)
    analysis: Mapped[float | None] = mapped_column(Float, nullable=True)
    partnership: Mapped[float | None] = mapped_column(Float, nullable=True)
    digital_literacy: Mapped[float | None] = mapped_column(Float, nullable=True)
    critical_thinking: Mapped[float | None] = mapped_column(Float, nullable=True)
    creativity: Mapped[float | None] = mapped_column(Float, nullable=True)
    communication: Mapped[float | None] = mapped_column(Float, nullable=True)
    teamwork: Mapped[float | None] = mapped_column(Float, nullable=True)
    emotional_intelligence: Mapped[float | None] = mapped_column(Float, nullable=True)
    adaptability: Mapped[float | None] = mapped_column(Float, nullable=True)
    self_education: Mapped[float | None] = mapped_column(Float, nullable=True)
    responsibility: Mapped[float | None] = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("ix_competency_specialty_year_course", "specialty", "year", "course"),
    )


class MotivatorProfile(Base):
    __tablename__ = "motivator_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    specialty: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    year: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    course: Mapped[str | None] = mapped_column(String(10), nullable=True)
    career: Mapped[float | None] = mapped_column(Float, nullable=True)
    altruism: Mapped[float | None] = mapped_column(Float, nullable=True)
    creativity: Mapped[float | None] = mapped_column(Float, nullable=True)
    money: Mapped[float | None] = mapped_column(Float, nullable=True)
    power: Mapped[float | None] = mapped_column(Float, nullable=True)
    independence: Mapped[float | None] = mapped_column(Float, nullable=True)
    knowledge: Mapped[float | None] = mapped_column(Float, nullable=True)
    communication: Mapped[float | None] = mapped_column(Float, nullable=True)
    recognition: Mapped[float | None] = mapped_column(Float, nullable=True)
    safety: Mapped[float | None] = mapped_column(Float, nullable=True)
    achievement: Mapped[float | None] = mapped_column(Float, nullable=True)
    self_development: Mapped[float | None] = mapped_column(Float, nullable=True)
    leadership: Mapped[float | None] = mapped_column(Float, nullable=True)
    teamwork: Mapped[float | None] = mapped_column(Float, nullable=True)
    stability: Mapped[float | None] = mapped_column(Float, nullable=True)
    challenge: Mapped[float | None] = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("ix_motivator_specialty_year_course", "specialty", "year", "course"),
    )


class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False
    )
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    z: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    device: Mapped[Device] = relationship(back_populates="readings")

    __table_args__ = (Index("ix_readings_device_created", "device_id", "created_at"),)
