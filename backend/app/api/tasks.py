"""Задачи и «Невидимая зарплата» / Tasks & invisible salary API."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.models_features import TaskLog, UserTask
from app.services.auth import get_current_user

router = APIRouter(tags=["tasks"])


class TaskCreate(BaseModel):
    name: str
    default_duration_minutes: int | None = None
    default_rate: float | None = None


class TaskUpdate(BaseModel):
    name: str | None = None
    default_duration_minutes: int | None = None
    default_rate: float | None = None


class TaskLogCreate(BaseModel):
    task_id: UUID | None = None
    duration_minutes: int
    rate: float | None = None
    log_date: date | None = None


@router.get("/tasks")
async def list_tasks(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserTask).where(UserTask.user_id == user.id))
    return [_task_dict(t) for t in result.scalars().all()]


@router.post("/tasks", status_code=201)
async def create_task(body: TaskCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task = UserTask(user_id=user.id, **body.model_dump())
    db.add(task)
    await db.flush()
    return _task_dict(task)


@router.put("/tasks/{task_id}")
async def update_task(
    task_id: UUID, body: TaskUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    task = await _get_task(db, user, task_id)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    await db.flush()
    return _task_dict(task)


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task = await _get_task(db, user, task_id)
    await db.delete(task)


@router.post("/task_logs", status_code=201)
async def create_log(body: TaskLogCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    log = TaskLog(
        user_id=user.id,
        task_id=body.task_id,
        duration_minutes=body.duration_minutes,
        rate=body.rate,
        log_date=body.log_date or date.today(),
    )
    db.add(log)
    await db.flush()
    return _log_dict(log)


@router.get("/task_logs")
async def list_logs(
    from_date: date | None = None,
    to_date: date | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(TaskLog).where(TaskLog.user_id == user.id)
    if from_date:
        q = q.where(TaskLog.log_date >= from_date)
    if to_date:
        q = q.where(TaskLog.log_date <= to_date)
    result = await db.execute(q.order_by(TaskLog.log_date.desc()))
    logs = result.scalars().all()
    grouped: dict[str, list] = {}
    for log in logs:
        key = log.log_date.isoformat()
        grouped.setdefault(key, []).append(_log_dict(log))
    return {"logs": [_log_dict(l) for l in logs], "by_day": grouped}


@router.get("/task_logs/report")
async def task_report(
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(TaskLog).where(TaskLog.user_id == user.id)
    if from_date:
        q = q.where(TaskLog.log_date >= from_date)
    if to_date:
        q = q.where(TaskLog.log_date <= to_date)
    result = await db.execute(q)
    logs = result.scalars().all()
    total_minutes = sum(l.duration_minutes for l in logs)
    total_money = sum((l.rate or 0) * l.duration_minutes / 60 for l in logs)
    return {
        "total_minutes": total_minutes,
        "total_hours": round(total_minutes / 60, 2),
        "total_money_saved": round(total_money, 2),
        "entries_count": len(logs),
    }


async def _get_task(db: AsyncSession, user: User, task_id: UUID) -> UserTask:
    result = await db.execute(select(UserTask).where(UserTask.id == task_id, UserTask.user_id == user.id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")
    return task


def _task_dict(t: UserTask) -> dict:
    return {
        "id": str(t.id),
        "name": t.name,
        "default_duration_minutes": t.default_duration_minutes,
        "default_rate": t.default_rate,
    }


def _log_dict(l: TaskLog) -> dict:
    return {
        "id": str(l.id),
        "task_id": str(l.task_id) if l.task_id else None,
        "duration_minutes": l.duration_minutes,
        "rate": l.rate,
        "log_date": l.log_date.isoformat(),
    }
