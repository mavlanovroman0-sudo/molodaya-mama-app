"""Трекер мамы / Mom baby tracker.

DEPRECATED: используйте `/api/v1/baby/*` (models_features). Эндпоинты `/mom/*`
сохранены для обратной совместимости и будут удалены в v2.1.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Baby, User
from app.schemas import (
    BabyCreate,
    BabyResponse,
    BabyTrackerSummary,
    DiaperLogCreate,
    FeedingLogCreate,
    SleepLogCreate,
)
from app.services.auth import get_current_user
from app.services.baby_tracker import (
    get_baby_or_404,
    get_tracker_summary,
    log_diaper,
    log_feeding,
    log_sleep,
)

router = APIRouter(prefix="/mom", tags=["mom-tracker"])


@router.get("/babies", response_model=list[BabyResponse])
async def list_babies(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Baby).where(Baby.user_id == user.id))
    return result.scalars().all()


@router.post("/babies", response_model=BabyResponse, status_code=201)
async def create_baby(
    body: BabyCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    baby = Baby(user_id=user.id, **body.model_dump())
    db.add(baby)
    await db.flush()
    return baby


@router.get("/babies/{baby_id}/summary", response_model=BabyTrackerSummary)
async def tracker_summary(
    baby_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        baby = await get_baby_or_404(db, baby_id, user)
    except ValueError:
        raise HTTPException(status_code=404, detail="Baby not found")
    return await get_tracker_summary(db, baby, user.language.value)


@router.post("/babies/{baby_id}/feeding", status_code=201)
async def add_feeding(
    baby_id: UUID,
    body: FeedingLogCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        baby = await get_baby_or_404(db, baby_id, user)
    except ValueError:
        raise HTTPException(status_code=404, detail="Baby not found")
    log = await log_feeding(db, baby, body.model_dump(exclude_none=True))
    return {"id": str(log.id)}


@router.post("/babies/{baby_id}/sleep", status_code=201)
async def add_sleep(
    baby_id: UUID,
    body: SleepLogCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        baby = await get_baby_or_404(db, baby_id, user)
    except ValueError:
        raise HTTPException(status_code=404, detail="Baby not found")
    log = await log_sleep(db, baby, body.model_dump(exclude_none=True))
    return {"id": str(log.id)}


@router.post("/babies/{baby_id}/diaper", status_code=201)
async def add_diaper(
    baby_id: UUID,
    body: DiaperLogCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        baby = await get_baby_or_404(db, baby_id, user)
    except ValueError:
        raise HTTPException(status_code=404, detail="Baby not found")
    log = await log_diaper(db, baby, body.model_dump(exclude_none=True))
    return {"id": str(log.id)}
