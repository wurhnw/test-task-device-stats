from datetime import datetime
from uuid import UUID

from app.db.session import SessionLocal
from app.services import analytics
from app.tasks.celery_app import celery_app


def _parse_dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _serialize(payload: dict) -> dict:
    def convert(obj):
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert(v) for v in obj]
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    return convert(payload)


@celery_app.task(name="analytics.device_stats")
def device_stats_task(device_id: str, period_from: str | None = None, period_to: str | None = None) -> dict:
    db = SessionLocal()
    try:
        result = analytics.compute_device_stats(
            db,
            device_id=UUID(device_id),
            period_from=_parse_dt(period_from),
            period_to=_parse_dt(period_to),
        )
    finally:
        db.close()
    return _serialize(result)


@celery_app.task(name="analytics.user_stats")
def user_stats_task(user_id: str, period_from: str | None = None, period_to: str | None = None) -> dict:
    db = SessionLocal()
    try:
        result = analytics.compute_user_stats(
            db,
            user_id=UUID(user_id),
            period_from=_parse_dt(period_from),
            period_to=_parse_dt(period_to),
        )
    finally:
        db.close()
    return _serialize(result)
