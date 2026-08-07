"""Middleware проверки подписки / Subscription enforcement middleware."""

import logging
from uuid import UUID

from jose import JWTError, jwt
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.config import settings
from app.database import async_session
from app.services.subscription import user_has_access

logger = logging.getLogger(__name__)

PUBLIC_PATHS = (
    "/health",
    "/health/ready",
    "/docs",
    "/redoc",
    "/openapi.json",
)

AUTH_EXEMPT_PREFIXES = (
    "/api/v1/auth",
    "/api/v1/webhook",
    "/api/v1/geo",
    "/api/v1/config",
    "/api/v1/internal",
)

SUBSCRIPTION_ALLOWED_PREFIXES = (
    "/api/v1/user/subscription-status",
    "/api/v1/subscription",
)

# Эндпоинты с X-Cron-Secret (без JWT); метод + точный путь
CRON_EXEMPT_ROUTES = (
    ("POST", "/api/v1/stores"),
    ("POST", "/api/v1/notifications/send"),
)


def _path_exempt(path: str, method: str = "GET") -> bool:
    if path in PUBLIC_PATHS or any(path.startswith(p) for p in AUTH_EXEMPT_PREFIXES):
        return True
    if any(path.startswith(p) for p in SUBSCRIPTION_ALLOWED_PREFIXES):
        return True
    if (method.upper(), path.rstrip("/") or path) in CRON_EXEMPT_ROUTES:
        return True
    # /api/v1/stores без trailing slash
    if method.upper() == "POST" and path.rstrip("/") == "/api/v1/stores":
        return True
    return not path.startswith("/api/v1")


class SubscriptionMiddleware:
    """Pure ASGI middleware (без BaseHTTPMiddleware — совместимость с async DB)."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not settings.subscription_enforce:
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        method = scope.get("method", "GET")
        if _path_exempt(path, method):
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        auth = request.headers.get("authorization", "")
        if not auth.lower().startswith("bearer "):
            response = JSONResponse(status_code=401, content={"detail": "Not authenticated"})
            await response(scope, receive, send)
            return

        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            user_id = UUID(payload["sub"])
        except (JWTError, ValueError, KeyError):
            response = JSONResponse(status_code=401, content={"detail": "Invalid token"})
            await response(scope, receive, send)
            return

        async with async_session() as db:
            has_access = await user_has_access(db, user_id)

        if not has_access:
            response = JSONResponse(
                status_code=403,
                content={
                    "detail": "Payment required — subscription or trial expired",
                    "code": "payment_required",
                },
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
