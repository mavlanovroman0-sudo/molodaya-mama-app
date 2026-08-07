"""Expo Push Notifications API."""

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.services.auth import get_current_user
from app.services.cron_auth import require_cron_secret
from app.services.expo_push import send_expo_push, send_expo_push_raw

router = APIRouter(prefix="/notifications", tags=["notifications"])


class RegisterToken(BaseModel):
    expo_push_token: str


class SendNotification(BaseModel):
    user_id: UUID | None = None
    token: str | None = None
    title: str
    body: str
    data: dict | None = None


@router.post("/register")
async def register_token(
    body: RegisterToken, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    user.expo_push_token = body.expo_push_token
    await db.flush()
    return {"status": "registered"}


@router.post("/send", dependencies=[Depends(require_cron_secret)])
async def send_notification(
    body: SendNotification,
    db: AsyncSession = Depends(get_db),
):
    ok = False
    if body.user_id:
        ok = await send_expo_push(db, body.user_id, body.title, body.body, body.data)
    elif body.token:
        ok = await send_expo_push_raw(body.token, body.title, body.body, body.data)
    return {"success": ok}
