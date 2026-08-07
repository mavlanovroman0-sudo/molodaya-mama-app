"""Бартер / Barter exchange API."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.models_features import BarterAd, BarterAdType, BarterTransaction, BarterTxStatus
from app.services.auth import get_current_user

router = APIRouter(prefix="/barter", tags=["barter"])


class AdCreate(BaseModel):
    title: str
    description: str | None = None
    ad_type: BarterAdType = BarterAdType.offer
    category: str | None = None
    location_lat: float | None = None
    location_lon: float | None = None


class AdUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_active: bool | None = None


class TxStatusUpdate(BaseModel):
    status: BarterTxStatus


@router.get("/ads")
async def list_ads(
    ad_type: BarterAdType | None = None,
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(BarterAd).where(BarterAd.is_active.is_(True))
    if ad_type:
        q = q.where(BarterAd.ad_type == ad_type)
    if category:
        q = q.where(BarterAd.category == category)
    result = await db.execute(q.order_by(BarterAd.created_at.desc()).limit(100))
    return [_ad_dict(a) for a in result.scalars().all()]


@router.post("/ads", status_code=201)
async def create_ad(body: AdCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ad = BarterAd(user_id=user.id, **body.model_dump())
    db.add(ad)
    await db.flush()
    return _ad_dict(ad)


@router.put("/ads/{ad_id}")
async def update_ad(
    ad_id: UUID, body: AdUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    ad = await _get_own_ad(db, user, ad_id)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(ad, k, v)
    await db.flush()
    return _ad_dict(ad)


@router.delete("/ads/{ad_id}", status_code=204)
async def delete_ad(ad_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ad = await _get_own_ad(db, user, ad_id)
    await db.delete(ad)


@router.post("/ads/{ad_id}/request", status_code=201)
async def request_exchange(
    ad_id: UUID,
    jetons_amount: int = Query(0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(BarterAd).where(BarterAd.id == ad_id, BarterAd.is_active.is_(True)))
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(404, "Ad not found")
    if ad.user_id == user.id:
        raise HTTPException(400, "Cannot request own ad")
    tx = BarterTransaction(
        ad_id=ad.id,
        from_user_id=user.id,
        to_user_id=ad.user_id,
        jetons_amount=jetons_amount,
    )
    db.add(tx)
    await db.flush()
    return _tx_dict(tx)


@router.get("/transactions")
async def list_transactions(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BarterTransaction).where(
            (BarterTransaction.from_user_id == user.id) | (BarterTransaction.to_user_id == user.id)
        )
    )
    return [_tx_dict(t) for t in result.scalars().all()]


@router.put("/transactions/{tx_id}/status")
async def update_tx_status(
    tx_id: UUID,
    body: TxStatusUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(BarterTransaction).where(BarterTransaction.id == tx_id))
    tx = result.scalar_one_or_none()
    if not tx or tx.to_user_id != user.id:
        raise HTTPException(404, "Transaction not found")
    tx.status = body.status
    await db.flush()
    return _tx_dict(tx)


async def _get_own_ad(db: AsyncSession, user: User, ad_id: UUID) -> BarterAd:
    result = await db.execute(select(BarterAd).where(BarterAd.id == ad_id, BarterAd.user_id == user.id))
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(404, "Ad not found")
    return ad


def _ad_dict(a: BarterAd) -> dict:
    return {
        "id": str(a.id),
        "user_id": str(a.user_id),
        "title": a.title,
        "description": a.description,
        "ad_type": a.ad_type.value,
        "category": a.category,
        "location_lat": a.location_lat,
        "location_lon": a.location_lon,
        "is_active": a.is_active,
    }


def _tx_dict(t: BarterTransaction) -> dict:
    return {
        "id": str(t.id),
        "ad_id": str(t.ad_id),
        "from_user_id": str(t.from_user_id),
        "to_user_id": str(t.to_user_id),
        "jetons_amount": t.jetons_amount,
        "status": t.status.value,
    }
