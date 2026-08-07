"""FCM push-уведомления / Firebase Cloud Messaging service."""

import logging
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import User

logger = logging.getLogger(__name__)

FCM_URL = "https://fcm.googleapis.com/fcm/send"


async def send_push_to_user(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    body: str,
    data: dict | None = None,
) -> bool:
    """Отправка push пользователю. Без FCM-ключа — логирует (MVP)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.fcm_token:
        logger.info("FCM skip user=%s (no token)", user_id)
        return False

    if not settings.fcm_server_key:
        logger.info("FCM mock → user=%s title=%s body=%s", user_id, title, body)
        return True

    payload = {
        "to": user.fcm_token,
        "notification": {"title": title, "body": body},
        "data": data or {},
    }
    headers = {
        "Authorization": f"key={settings.fcm_server_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(FCM_URL, json=payload, headers=headers)
        if resp.status_code != 200:
            logger.warning("FCM error %s: %s", resp.status_code, resp.text)
            return False
    return True
