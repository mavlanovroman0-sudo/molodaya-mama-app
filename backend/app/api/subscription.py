"""API подписки / Subscription API."""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import User
from app.services.auth import get_current_user
from app.services.payment import get_payment_provider
from app.services.subscription import (
    build_subscription_prices,
    build_subscription_status,
    get_latest_subscription,
    payment_already_processed,
)

router = APIRouter(tags=["subscription"])


class CheckoutRequest(BaseModel):
    plan: str  # monthly | yearly
    provider: str | None = None  # yookassa | rustore | tbank (опционально)


class VerifyRequest(BaseModel):
    payment_id: str


@router.get("/user/subscription-status")
async def subscription_status(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await build_subscription_status(db, user)


@router.get("/subscription/prices")
async def subscription_prices(
    request: Request,
    user: User = Depends(get_current_user),
):
    client_ip = request.client.host if request.client else None
    return await build_subscription_prices(user, client_ip=client_ip)


@router.post("/subscription/checkout")
async def create_checkout(
    body: CheckoutRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.plan not in ("monthly", "yearly"):
        raise HTTPException(400, "plan must be monthly or yearly")

    provider_name = (body.provider or settings.payment_provider or "yookassa").lower()
    country = user.country_code or "RU"

    if provider_name == "stripe":
        price_id = settings.stripe_price_id(country, body.plan)
        if not price_id:
            raise HTTPException(
                503,
                f"Stripe price not configured for {country}/{body.plan}. "
                "Set STRIPE_PRICE_* env vars or switch PAYMENT_PROVIDER=yookassa.",
            )
    else:
        price_id = ""

    try:
        provider = get_payment_provider(provider_name)
    except RuntimeError as e:
        raise HTTPException(503, str(e)) from e

    try:
        url = await provider.create_checkout_session(
            user.id,
            user.email,
            price_id,
            country,
            body.plan,
        )
    except RuntimeError as e:
        raise HTTPException(503, str(e)) from e

    return {"checkout_url": url, "provider": provider_name}


@router.post("/subscription/verify")
async def verify_subscription(
    body: VerifyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Проверка оплаты после deep link / return URL (RuStore, YooKassa и др.)."""
    processed = await payment_already_processed(db, body.payment_id)
    status = await build_subscription_status(db, user)
    sub = await get_latest_subscription(db, user.id)
    belongs_to_user = bool(
        sub
        and (
            sub.provider_payment_id == body.payment_id
            or sub.provider_subscription_id == body.payment_id
        )
    )
    return {
        "verified": processed and belongs_to_user,
        "payment_id": body.payment_id,
        "subscription": status,
    }


@router.post("/subscription/cancel")
async def cancel_subscription(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from app.models_subscription import SubscriptionStatus
    from app.services.subscription import cancel_subscription_record

    sub = await get_latest_subscription(db, user.id)
    if (
        not sub
        or not sub.provider_subscription_id
        or sub.status != SubscriptionStatus.active
        or sub.provider in ("internal", "")
    ):
        raise HTTPException(404, "No active paid subscription")

    try:
        provider = get_payment_provider(sub.provider)
        await provider.cancel_subscription(sub.provider_subscription_id)
    except RuntimeError:
        # Одноразовые провайдеры: локальная отмена автопродления до end_date
        pass

    await cancel_subscription_record(db, sub.provider_subscription_id)
    return {"status": "cancel_scheduled", "access_until": sub.end_date.isoformat() if sub.end_date else None}
