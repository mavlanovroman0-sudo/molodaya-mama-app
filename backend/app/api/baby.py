"""Трекеры малыша / Baby tracker API."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.models_features import BabyChecklist, BabyDiaper, BabyFeed, BabySleep
from app.services.auth import get_current_user

router = APIRouter(prefix="/baby", tags=["baby"])


class FeedCreate(BaseModel):
    baby_name: str = "Малыш"
    feed_type: str = "breast"
    volume_ml: int | None = None
    duration_minutes: int | None = None
    notes: str | None = None
    feed_time: datetime | None = None


class FeedUpdate(BaseModel):
    feed_type: str | None = None
    volume_ml: int | None = None
    duration_minutes: int | None = None
    notes: str | None = None


class SleepCreate(BaseModel):
    baby_name: str = "Малыш"
    start_time: datetime
    end_time: datetime | None = None
    quality: int | None = None
    notes: str | None = None


class SleepUpdate(BaseModel):
    end_time: datetime | None = None
    quality: int | None = None
    notes: str | None = None


class DiaperCreate(BaseModel):
    baby_name: str = "Малыш"
    diaper_type: str = "wet"
    change_time: datetime | None = None
    notes: str | None = None


class DiaperUpdate(BaseModel):
    diaper_type: str | None = None
    notes: str | None = None


class ChecklistCreate(BaseModel):
    baby_name: str = "Малыш"
    age_months: int = 0
    item_name: str


class ChecklistUpdate(BaseModel):
    is_bought: bool | None = None
    item_name: str | None = None


# --- Feeds ---

@router.get("/feeds")
async def list_feeds(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BabyFeed).where(BabyFeed.user_id == user.id).order_by(BabyFeed.feed_time.desc()).limit(100)
    )
    return [_feed_dict(f) for f in result.scalars().all()]


@router.post("/feeds", status_code=201)
async def create_feed(body: FeedCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    feed = BabyFeed(user_id=user.id, **body.model_dump())
    db.add(feed)
    await db.flush()
    return _feed_dict(feed)


@router.put("/feeds/{feed_id}")
async def update_feed(
    feed_id: UUID, body: FeedUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    feed = await _get_feed(db, user, feed_id)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(feed, k, v)
    await db.flush()
    return _feed_dict(feed)


@router.delete("/feeds/{feed_id}", status_code=204)
async def delete_feed(feed_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    feed = await _get_feed(db, user, feed_id)
    await db.delete(feed)


# --- Sleep ---

@router.get("/sleep")
async def list_sleep(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BabySleep).where(BabySleep.user_id == user.id).order_by(BabySleep.start_time.desc()).limit(100)
    )
    return [_sleep_dict(s) for s in result.scalars().all()]


@router.post("/sleep", status_code=201)
async def create_sleep(body: SleepCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sleep = BabySleep(user_id=user.id, **body.model_dump())
    db.add(sleep)
    await db.flush()
    return _sleep_dict(sleep)


@router.put("/sleep/{sleep_id}")
async def update_sleep(
    sleep_id: UUID, body: SleepUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    sleep = await _get_sleep(db, user, sleep_id)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(sleep, k, v)
    await db.flush()
    return _sleep_dict(sleep)


@router.delete("/sleep/{sleep_id}", status_code=204)
async def delete_sleep(sleep_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sleep = await _get_sleep(db, user, sleep_id)
    await db.delete(sleep)


# --- Diapers ---

@router.get("/diapers")
async def list_diapers(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BabyDiaper).where(BabyDiaper.user_id == user.id).order_by(BabyDiaper.change_time.desc()).limit(100)
    )
    return [_diaper_dict(d) for d in result.scalars().all()]


@router.post("/diapers", status_code=201)
async def create_diaper(body: DiaperCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    diaper = BabyDiaper(user_id=user.id, **body.model_dump())
    db.add(diaper)
    await db.flush()
    return _diaper_dict(diaper)


@router.put("/diapers/{diaper_id}")
async def update_diaper(
    diaper_id: UUID, body: DiaperUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    diaper = await _get_diaper(db, user, diaper_id)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(diaper, k, v)
    await db.flush()
    return _diaper_dict(diaper)


@router.delete("/diapers/{diaper_id}", status_code=204)
async def delete_diaper(
    diaper_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    diaper = await _get_diaper(db, user, diaper_id)
    await db.delete(diaper)


# --- Checklist ---

@router.get("/checklist")
async def list_checklist(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BabyChecklist).where(BabyChecklist.user_id == user.id))
    return [_chk_dict(c) for c in result.scalars().all()]


@router.post("/checklist", status_code=201)
async def create_checklist_item(
    body: ChecklistCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    item = BabyChecklist(user_id=user.id, **body.model_dump())
    db.add(item)
    await db.flush()
    return _chk_dict(item)


@router.put("/checklist/{item_id}")
async def update_checklist_item(
    item_id: UUID, body: ChecklistUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    item = await _get_chk(db, user, item_id)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    await db.flush()
    return _chk_dict(item)


@router.delete("/checklist/{item_id}", status_code=204)
async def delete_checklist_item(
    item_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    item = await _get_chk(db, user, item_id)
    await db.delete(item)


async def _get_feed(db, user, fid):
    r = await db.execute(select(BabyFeed).where(BabyFeed.id == fid, BabyFeed.user_id == user.id))
    o = r.scalar_one_or_none()
    if not o:
        raise HTTPException(404)
    return o


async def _get_sleep(db, user, sid):
    r = await db.execute(select(BabySleep).where(BabySleep.id == sid, BabySleep.user_id == user.id))
    o = r.scalar_one_or_none()
    if not o:
        raise HTTPException(404)
    return o


async def _get_diaper(db, user, did):
    r = await db.execute(select(BabyDiaper).where(BabyDiaper.id == did, BabyDiaper.user_id == user.id))
    o = r.scalar_one_or_none()
    if not o:
        raise HTTPException(404)
    return o


async def _get_chk(db, user, cid):
    r = await db.execute(select(BabyChecklist).where(BabyChecklist.id == cid, BabyChecklist.user_id == user.id))
    o = r.scalar_one_or_none()
    if not o:
        raise HTTPException(404)
    return o


def _feed_dict(f): return {"id": str(f.id), "baby_name": f.baby_name, "feed_type": f.feed_type, "volume_ml": f.volume_ml, "duration_minutes": f.duration_minutes, "notes": f.notes, "feed_time": f.feed_time.isoformat() if f.feed_time else None}
def _sleep_dict(s): return {"id": str(s.id), "baby_name": s.baby_name, "start_time": s.start_time.isoformat(), "end_time": s.end_time.isoformat() if s.end_time else None, "quality": s.quality, "notes": s.notes}
def _diaper_dict(d): return {"id": str(d.id), "baby_name": d.baby_name, "diaper_type": d.diaper_type, "change_time": d.change_time.isoformat() if d.change_time else None, "notes": d.notes}
def _chk_dict(c): return {"id": str(c.id), "baby_name": c.baby_name, "age_months": c.age_months, "item_name": c.item_name, "is_bought": c.is_bought}
