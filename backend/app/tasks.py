"""Фоновые задачи / Background tasks (Celery + APScheduler)."""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.config import settings
from app.database import async_session
from app.models import Referral, User
from app.services.expo_push import send_expo_push

logger = logging.getLogger(__name__)


async def send_invite_reminder() -> dict:
    """
    Находит пользователей старше 7 дней без успешных рефералов (как пригласивших)
    и отправляет push-напоминание.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    sent = 0
    skipped = 0

    async with async_session() as db:
        # Пользователи без ни одного приглашённого друга (referee_id IS NOT NULL)
        subq = select(Referral.referrer_id).where(Referral.referee_id.isnot(None))
        result = await db.execute(
            select(User).where(
                User.created_at <= cutoff,
                User.id.notin_(subq),
            )
        )
        users = result.scalars().all()

        for user in users:
            ok = await send_expo_push(
                db,
                user.id,
                title="молодая мама",
                body="Пригласите друзей и получите бонусы!",
                data={"type": "invite_reminder"},
            )
            if ok:
                sent += 1
            else:
                skipped += 1

        await db.commit()

    logger.info("invite_reminder sent=%s skipped=%s", sent, skipped)
    return {"sent": sent, "skipped": skipped, "total_candidates": sent + skipped}


def send_invite_reminder_sync() -> dict:
    """Обёртка для Celery (sync)."""
    import asyncio

    return asyncio.run(send_invite_reminder())
