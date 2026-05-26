from datetime import datetime
from statistics import median
from uuid import UUID

from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.models import CompetencyProfile, Device, MotivatorProfile, Reading


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


def get_competency_by_specialties(
    db: Session,
    specialties: List[str],
    year: str,
    course: str | None = None,
) -> List[dict]:
    if not specialties:
        return []

    competency_fields = [
        "leadership", "analysis", "partnership",
        "digital_literacy", "critical_thinking", "creativity",
        "communication", "teamwork", "emotional_intelligence",
        "adaptability", "self_education", "responsibility",
    ]

    result = []

    for specialty in specialties:
        stmt = select(
            func.avg(CompetencyProfile.leadership).label("leadership"),
            func.avg(CompetencyProfile.analysis).label("analysis"),
            func.avg(CompetencyProfile.partnership).label("partnership"),
            func.avg(CompetencyProfile.digital_literacy).label("digital_literacy"),
            func.avg(CompetencyProfile.critical_thinking).label("critical_thinking"),
            func.avg(CompetencyProfile.creativity).label("creativity"),
            func.avg(CompetencyProfile.communication).label("communication"),
            func.avg(CompetencyProfile.teamwork).label("teamwork"),
            func.avg(CompetencyProfile.emotional_intelligence).label("emotional_intelligence"),
            func.avg(CompetencyProfile.adaptability).label("adaptability"),
            func.avg(CompetencyProfile.self_education).label("self_education"),
            func.avg(CompetencyProfile.responsibility).label("responsibility"),
        ).where(
            CompetencyProfile.specialty == specialty,
            CompetencyProfile.year == year,
        )

        if course is not None:
            stmt = stmt.where(CompetencyProfile.course == course)

        row = db.execute(stmt).one()

        has_data = any(row[field] is not None for field in competency_fields)
        if has_data:
            entry = {"specialty": specialty}
            for field in competency_fields:
                value = getattr(row, field)
                entry[field] = round(value) if value is not None else None
            result.append(entry)

    return result


def get_motivator_profile_by_specialties(
    db: Session,
    specialties: List[str],
    year: str,
    course: str | None = None,
) -> List[dict]:
    if not specialties:
        return []

    motivator_fields = [
        "career", "altruism", "creativity",
        "money", "power", "independence",
        "knowledge", "communication", "recognition",
        "safety", "achievement", "self_development",
        "leadership", "teamwork", "stability", "challenge",
    ]

    result = []

    for specialty in specialties:
        stmt = select(
            func.avg(MotivatorProfile.career).label("career"),
            func.avg(MotivatorProfile.altruism).label("altruism"),
            func.avg(MotivatorProfile.creativity).label("creativity"),
            func.avg(MotivatorProfile.money).label("money"),
            func.avg(MotivatorProfile.power).label("power"),
            func.avg(MotivatorProfile.independence).label("independence"),
            func.avg(MotivatorProfile.knowledge).label("knowledge"),
            func.avg(MotivatorProfile.communication).label("communication"),
            func.avg(MotivatorProfile.recognition).label("recognition"),
            func.avg(MotivatorProfile.safety).label("safety"),
            func.avg(MotivatorProfile.achievement).label("achievement"),
            func.avg(MotivatorProfile.self_development).label("self_development"),
            func.avg(MotivatorProfile.leadership).label("leadership"),
            func.avg(MotivatorProfile.teamwork).label("teamwork"),
            func.avg(MotivatorProfile.stability).label("stability"),
            func.avg(MotivatorProfile.challenge).label("challenge"),
        ).where(
            MotivatorProfile.specialty == specialty,
            MotivatorProfile.year == year,
        )

        if course is not None:
            stmt = stmt.where(MotivatorProfile.course == course)

        row = db.execute(stmt).one()

        has_data = any(row[field] is not None for field in motivator_fields)
        if has_data:
            entry = {"specialty": specialty}
            for field in motivator_fields:
                value = getattr(row, field)
                entry[field] = round(value) if value is not None else None
            result.append(entry)

    return result
