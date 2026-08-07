"""Внутренние cron-эндпоинты / Internal scheduled task triggers."""

from fastapi import APIRouter, Depends

from app.services.cron_auth import require_cron_secret
from app.tasks import send_invite_reminder

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/cron/invite-reminder", dependencies=[Depends(require_cron_secret)])
async def cron_invite_reminder():
    """
    Ручной/cron запуск напоминаний о приглашении друзей.
    Заголовок: X-Cron-Secret: <CRON_SECRET из .env>
    """
    return await send_invite_reminder()
