"""Expo Push Notifications (бесплатно) / Expo push service."""

import logging
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User

logger = logging.getLogger(__name__)

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


async def send_expo_push(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    body: str,
    data: dict | None = None,
) -> bool:
    """Отправка через Expo Push API (бесплатно)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    token = user.expo_push_token if user else None
    if not token or not token.startswith("ExponentPushToken"):
        logger.info("Expo push skip user=%s (no valid token)", user_id)
        return False

    payload = {
        "to": token,
        "title": title,
        "body": body,
        "data": data or {},
        "sound": "default",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                EXPO_PUSH_URL,
                json=payload,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
            )
            if resp.status_code != 200:
                logger.warning("Expo push error %s: %s", resp.status_code, resp.text)
                return False
            result_json = resp.json()
            if result_json.get("data", [{}])[0].get("status") == "error":
                logger.warning("Expo push rejected: %s", result_json)
                return False
    except httpx.HTTPError as e:
        logger.warning("Expo push failed: %s", e)
        return False
    return True


async def send_expo_push_raw(token: str, title: str, body: str, data: dict | None = None) -> bool:
    """Прямая отправка по токену."""
    if not token:
        return False
    payload = {"to": token, "title": title, "body": body, "data": data or {}}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(EXPO_PUSH_URL, json=payload)
        return resp.status_code == 200
