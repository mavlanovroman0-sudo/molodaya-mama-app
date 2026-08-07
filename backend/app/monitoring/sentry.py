"""Инициализация Sentry (только production + SENTRY_DSN)."""

from __future__ import annotations

import logging

from app.config import settings

logger = logging.getLogger(__name__)


def init_sentry() -> None:
    """Подключить Sentry при APP_ENV=production и заданном SENTRY_DSN."""
    if settings.app_env.lower() != "production":
        return
    if not settings.sentry_dsn:
        logger.info("SENTRY_DSN not set — Sentry disabled")
        return

    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.app_env,
        integrations=[
            StarletteIntegration(),
            FastApiIntegration(),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )
    logger.info("Sentry initialized for production")
