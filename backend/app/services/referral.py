"""Реферальная система / Referral service."""

import secrets
import string
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Referral, User
from app.services.tokens import add_jetons

CODE_ALPHABET = string.ascii_uppercase + string.digits


def generate_referral_code(length: int = 8) -> str:
    """Генерация уникального реферального кода (до 20 символов)."""
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(length))


async def ensure_unique_code(db: AsyncSession) -> str:
    for _ in range(10):
        code = generate_referral_code()
        exists = await db.execute(select(User.id).where(User.referral_code == code))
        if not exists.scalar_one_or_none():
            return code
    return generate_referral_code(12)


async def get_or_create_referral_code(db: AsyncSession, user: User) -> str:
    if user.referral_code:
        return user.referral_code
    code = await ensure_unique_code(db)
    user.referral_code = code
    await db.flush()
    return code


async def apply_referral_code(
    db: AsyncSession,
    referee: User,
    referral_code: str,
    referee_id: UUID | None = None,
) -> dict:
    """
    Применяет реферальный код для текущего (нового) пользователя.
    referee_id в теле — опционально, по умолчанию текущий user.
    """
    code = referral_code.strip().upper()
    if not code:
        raise ValueError("invalid_code")

    target_id = referee_id or referee.id
    if target_id != referee.id:
        raise ValueError("referee_mismatch")

    referrer_result = await db.execute(select(User).where(User.referral_code == code))
    referrer = referrer_result.scalar_one_or_none()
    if not referrer:
        raise ValueError("code_not_found")
    if referrer.id == referee.id:
        raise ValueError("self_referral")

    existing = await db.execute(
        select(Referral).where(Referral.referee_id == referee.id)
    )
    if existing.scalar_one_or_none():
        raise ValueError("already_referred")

    now = datetime.now(timezone.utc)
    referral = Referral(
        referrer_id=referrer.id,
        referee_id=referee.id,
        referral_code=code,
        used_at=now,
        bonus_given=True,
    )
    db.add(referral)

    await add_jetons(db, referrer, settings.referral_bonus_referrer, "referral_referrer")
    await add_jetons(db, referee, settings.referral_bonus_referee, "referral_referee")
    await db.flush()

    return {
        "referrer_id": str(referrer.id),
        "referee_id": str(referee.id),
        "bonus_referrer": settings.referral_bonus_referrer,
        "bonus_referee": settings.referral_bonus_referee,
    }


async def get_referral_stats(db: AsyncSession, user: User) -> dict:
    count_result = await db.execute(
        select(func.count(Referral.id)).where(
            Referral.referrer_id == user.id,
            Referral.referee_id.isnot(None),
            Referral.bonus_given.is_(True),
        )
    )
    invited_count = count_result.scalar() or 0
    tokens_earned = invited_count * settings.referral_bonus_referrer
    return {
        "referral_code": user.referral_code,
        "invited_count": invited_count,
        "tokens_earned": tokens_earned,
    }
