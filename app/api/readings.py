from datetime import datetime
from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Device, Reading
from app.schemas.schemas import ReadingCreate, ReadingRead, StatsResponse, TaskAccepted, TaskResult, UserStatsResponse
from app.services import analytics
from app.tasks.analytics_tasks import device_stats_task, user_stats_task
from app.tasks.celery_app import celery_app

router = APIRouter(tags=["readings"])


@router.post(
    "/devices/{device_id}/readings",
    response_model=ReadingRead,
    status_code=status.HTTP_201_CREATED,
)
def create_reading(device_id: UUID, payload: ReadingCreate, db: Session = Depends(get_db)) -> Reading:
    if db.get(Device, device_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    reading = Reading(device_id=device_id, x=payload.x, y=payload.y, z=payload.z)
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.get("/devices/{device_id}/stats", response_model=StatsResponse)
def device_stats(
    device_id: UUID,
    period_from: datetime | None = Query(default=None),
    period_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict:
    if db.get(Device, device_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return analytics.compute_device_stats(db, device_id, period_from, period_to)


@router.post("/devices/{device_id}/stats/async", response_model=TaskAccepted, status_code=status.HTTP_202_ACCEPTED)
def device_stats_async(
    device_id: UUID,
    period_from: datetime | None = Query(default=None),
    period_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> TaskAccepted:
    if db.get(Device, device_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    task = device_stats_task.delay(
        str(device_id),
        period_from.isoformat() if period_from else None,
        period_to.isoformat() if period_to else None,
    )
    return TaskAccepted(task_id=task.id)


@router.get("/users/{user_id}/stats", response_model=UserStatsResponse)
def user_stats(
    user_id: UUID,
    period_from: datetime | None = Query(default=None),
    period_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict:
    return analytics.compute_user_stats(db, user_id, period_from, period_to)


@router.post("/users/{user_id}/stats/async", response_model=TaskAccepted, status_code=status.HTTP_202_ACCEPTED)
def user_stats_async(
    user_id: UUID,
    period_from: datetime | None = Query(default=None),
    period_to: datetime | None = Query(default=None),
) -> TaskAccepted:
    task = user_stats_task.delay(
        str(user_id),
        period_from.isoformat() if period_from else None,
        period_to.isoformat() if period_to else None,
    )
    return TaskAccepted(task_id=task.id)


@router.get("/tasks/{task_id}", response_model=TaskResult)
def task_status(task_id: str) -> TaskResult:
    async_result = AsyncResult(task_id, app=celery_app)
    result = async_result.result if async_result.successful() else None
    return TaskResult(task_id=task_id, status=async_result.status, result=result)
