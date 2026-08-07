"""HomeEase 2.0 API — FastAPI application."""

import logging
import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.logging_config import setup_logging

setup_logging(settings.app_env)

from app.monitoring.sentry import init_sentry

init_sentry()
from app.database import Base, engine
import app.models  # noqa: F401 — регистрация ORM-моделей в metadata
from app.models import (  # noqa: F401 — явный импорт для Alembic/тестов
    Baby,
    Barter,
    BleDevice,
    DiaperLog,
    FavoriteStore,
    FeedingLog,
    Referral,
    RoleProfile,
    SleepLog,
    SmartDevice,
    Store,
    StressScore,
    TokenTransaction,
    User,
    VehicleSettings,
)
from app.api import (
    baby,
    barter,
    health as health_api,
    notifications,
    referral as referral_api,
    shopping,
    smart_home as local_smart_home,
    subscription as subscription_api,
    tasks as tasks_api,
    user_geo,
    webhooks,
)
from app.middleware.subscription import SubscriptionMiddleware
from app.routers import ai, auth, ble, geo, internal, mom, remote_config, roles, smart_home, stores
import app.models_features  # noqa: F401
import app.models_subscription  # noqa: F401
from app.database import async_session
from app.services.subscription import expire_due_subscriptions
from app.tasks import send_invite_reminder

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None
_IS_PRODUCTION = settings.app_env.lower() == "production"


async def _expire_subscriptions_job() -> None:
    async with async_session() as db:
        n = await expire_due_subscriptions(db)
        await db.commit()
        if n:
            logger.info("Expired %s subscription(s)", n)


def _cors_origins() -> list[str]:
    """В разработке — любой origin (Starlette отражает Origin при credentials)."""
    if _IS_PRODUCTION:
        return settings.cors_origin_list
    return ["*"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler
    if not _IS_PRODUCTION:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    if settings.enable_scheduler:
        _scheduler = AsyncIOScheduler()
        _scheduler.add_job(send_invite_reminder, "cron", hour=10, minute=0, id="invite_reminder")
        _scheduler.add_job(
            _expire_subscriptions_job, "cron", hour=1, minute=0, id="expire_subscriptions"
        )
        _scheduler.start()

    yield

    if _scheduler:
        _scheduler.shutdown(wait=False)
    await engine.dispose()


_docs = None if _IS_PRODUCTION else "/docs"
_redoc = None if _IS_PRODUCTION else "/redoc"
_openapi = None if _IS_PRODUCTION else "/openapi.json"

app = FastAPI(
    title="HomeEase 2.0 API",
    description="""
Кроссплатформенное супер-приложение для домохозяек и молодых мам.

## Возможности
- Двухролевая архитектура (Домохозяйка / Молодая мама)
- Автоопределение языка (6 языков) и геолокация района
- Избранные магазины и единая доставка
- Умный дом (Home Assistant, Яндекс, Google)
- Трекер малыша с AI-прогнозами
- BLE брелок «Красная кнопка»
- Реферальная система и органический рост
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url=_docs,
    redoc_url=_redoc,
    openapi_url=_openapi,
)

_origins = _cors_origins()
if _IS_PRODUCTION and not _origins:
    raise RuntimeError(
        "Production requires non-empty CORS_ORIGINS "
        "(comma-separated https origins, not '*')"
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SubscriptionMiddleware)

app.include_router(health_api.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    if _IS_PRODUCTION:
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    return JSONResponse(status_code=500, content={"detail": str(exc), "type": type(exc).__name__})


app.include_router(auth.router, prefix="/api/v1")
app.include_router(geo.router, prefix="/api/v1")
app.include_router(roles.router, prefix="/api/v1")
app.include_router(stores.router, prefix="/api/v1")
app.include_router(smart_home.router, prefix="/api/v1")
app.include_router(mom.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(ble.router, prefix="/api/v1")
app.include_router(referral_api.router, prefix="/api/v1")
app.include_router(shopping.router, prefix="/api/v1")
app.include_router(barter.router, prefix="/api/v1")
app.include_router(tasks_api.router, prefix="/api/v1")
app.include_router(local_smart_home.router, prefix="/api/v1")
app.include_router(baby.router, prefix="/api/v1")
app.include_router(user_geo.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(subscription_api.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(remote_config.router, prefix="/api/v1")
app.include_router(internal.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "app": "HomeEase 2.0"}
