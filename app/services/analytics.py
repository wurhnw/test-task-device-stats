from datetime import datetime
from statistics import median
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Device, Reading


def _axis_stats(values: list[float]) -> dict:
    if not values:
        return {"min": None, "max": None, "count": 0, "sum": 0.0, "median": None}
    return {
        "min": min(values),
        "max": max(values),
        "count": len(values),
        "sum": sum(values),
        "median": median(values),
    }


def _fetch_readings(
    db: Session,
    device_id: UUID | None = None,
    user_id: UUID | None = None,
    period_from: datetime | None = None,
    period_to: datetime | None = None,
) -> list[Reading]:
    stmt = select(Reading)
    if device_id is not None:
        stmt = stmt.where(Reading.device_id == device_id)
    if user_id is not None:
        stmt = stmt.join(Device, Device.id == Reading.device_id).where(Device.user_id == user_id)
    if period_from is not None:
        stmt = stmt.where(Reading.created_at >= period_from)
    if period_to is not None:
        stmt = stmt.where(Reading.created_at <= period_to)
    return list(db.scalars(stmt))


def _build_stats(
    readings: list[Reading],
    device_id: UUID | None,
    period_from: datetime | None,
    period_to: datetime | None,
) -> dict:
    return {
        "device_id": device_id,
        "period_from": period_from,
        "period_to": period_to,
        "x": _axis_stats([r.x for r in readings]),
        "y": _axis_stats([r.y for r in readings]),
        "z": _axis_stats([r.z for r in readings]),
    }


def compute_device_stats(
    db: Session,
    device_id: UUID,
    period_from: datetime | None = None,
    period_to: datetime | None = None,
) -> dict:
    readings = _fetch_readings(db, device_id=device_id, period_from=period_from, period_to=period_to)
    return _build_stats(readings, device_id, period_from, period_to)


def compute_user_stats(
    db: Session,
    user_id: UUID,
    period_from: datetime | None = None,
    period_to: datetime | None = None,
) -> dict:
    devices = list(db.scalars(select(Device).where(Device.user_id == user_id)))
    per_device = [
        _build_stats(
            _fetch_readings(db, device_id=d.id, period_from=period_from, period_to=period_to),
            d.id,
            period_from,
            period_to,
        )
        for d in devices
    ]
    aggregated_readings = _fetch_readings(
        db, user_id=user_id, period_from=period_from, period_to=period_to
    )
    aggregated = _build_stats(aggregated_readings, None, period_from, period_to)
    return {
        "user_id": user_id,
        "period_from": period_from,
        "period_to": period_to,
        "aggregated": aggregated,
        "per_device": per_device,
    }
