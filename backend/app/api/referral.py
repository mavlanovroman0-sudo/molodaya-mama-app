"""Реферальные эндпоинты / Referral API."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.services.auth import get_current_user
from app.services.referral import apply_referral_code, get_or_create_referral_code, get_referral_stats

router = APIRouter(prefix="/referral", tags=["referral"])


class ReferralCodeResponse(BaseModel):
    referral_code: str


class ReferralApplyRequest(BaseModel):
    referral_code: str = Field(min_length=3, max_length=20)
    referee_id: UUID | None = None


class ReferralApplyResponse(BaseModel):
    success: bool
    referrer_id: str
    referee_id: str
    bonus_referrer: int
    bonus_referee: int


class ReferralStatsResponse(BaseModel):
    referral_code: str | None
    invited_count: int
    tokens_earned: int


@router.post("/generate", response_model=ReferralCodeResponse)
async def generate_code(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Генерирует или возвращает существующий реферальный код."""
    code = await get_or_create_referral_code(db, user)
    return ReferralCodeResponse(referral_code=code)


@router.post("/apply", response_model=ReferralApplyResponse)
async def apply_code(
    body: ReferralApplyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Применяет реферальный код для текущего пользователя."""
    try:
        result = await apply_referral_code(db, user, body.referral_code, body.referee_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ReferralApplyResponse(success=True, **result)


@router.get("/stats", response_model=ReferralStatsResponse)
async def referral_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Статистика приглашений и заработанных жетонов."""
    await get_or_create_referral_code(db, user)
    stats = await get_referral_stats(db, user)
    return ReferralStatsResponse(**stats)
