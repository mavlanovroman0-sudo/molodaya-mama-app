"""Проверка внутренних cron-запросов / Internal cron auth."""

import hmac

from fastapi import Header, HTTPException

from app.config import settings


def require_cron_secret(x_cron_secret: str | None = Header(default=None)) -> None:
    expected = settings.cron_secret or ""
    provided = x_cron_secret or ""
    if not expected or not hmac.compare_digest(provided, expected):
        raise HTTPException(status_code=403, detail="Invalid cron secret")
