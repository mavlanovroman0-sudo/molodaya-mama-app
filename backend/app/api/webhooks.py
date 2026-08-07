"""Платёжные webhooks / Payment webhooks."""

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models_subscription import SubscriptionPlan
from app.services.payment import StripePaymentProvider
from app.services.subscription import (
    activate_paid_subscription,
    cancel_subscription_record,
    payment_already_processed,
    renew_subscription_period,
)
from app.services.rustore_provider import RuStoreProvider
from app.services.tbank_provider import TBankProvider
from app.services.yookassa_provider import YooKassaProvider, subscription_period_end

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhooks"])


@router.post("/yookassa")
async def yookassa_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Webhook YooKassa: только верифицированные события."""
    payload = await request.body()
    yk = YooKassaProvider()

    if not yk.is_available():
        raise HTTPException(503, "YooKassa is not configured")

    try:
        parsed = await yk.handle_webhook(payload)
        event_name = parsed.get("event", "")
        payment = parsed.get("object") or {}
    except Exception as e:
        logger.warning("YooKassa webhook error: %s", e)
        raise HTTPException(400, "Invalid webhook") from e

    # Активация только после реальной оплаты (не waiting_for_capture)
    if event_name == "payment.succeeded":
        await _handle_yookassa_payment_succeeded(db, payment)
    elif event_name == "payment.canceled":
        await _handle_yookassa_payment_canceled(db, payment)
    else:
        logger.info("Unhandled YooKassa event: %s", event_name)

    return {"received": True}


async def _handle_yookassa_payment_succeeded(db: AsyncSession, payment: dict) -> None:
    if payment.get("status") != "succeeded":
        return

    metadata = payment.get("metadata") or {}
    user_id = metadata.get("user_id")
    plan_str = metadata.get("plan", "monthly")
    payment_id = payment.get("id")

    if not user_id or not payment_id:
        logger.warning("YooKassa payment missing metadata: %s", payment_id)
        return

    if await payment_already_processed(db, str(payment_id)):
        logger.info("YooKassa payment %s already processed (idempotent skip)", payment_id)
        return

    plan = SubscriptionPlan.yearly if plan_str == "yearly" else SubscriptionPlan.monthly
    period_end = subscription_period_end(plan_str)
    customer_id = (payment.get("payment_method") or {}).get("id")

    await activate_paid_subscription(
        db,
        UUID(user_id),
        plan,
        str(payment_id),
        str(customer_id) if customer_id else None,
        period_end,
        provider="yookassa",
        provider_payment_id=str(payment_id),
        yookassa_payment_method_id=str(customer_id) if customer_id else None,
    )


async def _handle_yookassa_payment_canceled(db: AsyncSession, payment: dict) -> None:
    """Отмена незавершённого платежа: не трогаем уже активную подписку с другим id."""
    payment_id = payment.get("id")
    status = payment.get("status")
    if payment_id and status == "canceled":
        # Только если подписка была привязана к этому payment id и ещё не оплачена
        if not await payment_already_processed(db, str(payment_id)):
            await cancel_subscription_record(db, str(payment_id))


@router.post("/rustore")
async def rustore_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Webhook RuStore: только расшифрованный payload при настроенном секрете."""
    payload = await request.body()
    rs = RuStoreProvider()

    if not rs.is_available():
        raise HTTPException(503, "RuStore is not configured")

    try:
        event = rs.construct_webhook_event(payload)
    except Exception as e:
        logger.warning("RuStore webhook parse error: %s", e)
        raise HTTPException(400, "Invalid webhook") from e

    obj = event.get("object") or event
    parsed = rs.parse_subscription_event(obj)
    event_type = parsed.get("event_type", "")

    if parsed.get("activated") and parsed.get("purchase_id"):
        metadata = obj.get("metadata") or {}
        user_id = (
            metadata.get("user_id")
            or obj.get("user_id")
            or obj.get("appUserId")
            or obj.get("app_user_id")
        )
        plan_str = metadata.get("plan") or (
            "yearly" if "yearly" in str(parsed.get("product_code", "")).lower() else "monthly"
        )
        purchase_id = str(parsed["purchase_id"])
        period_end = subscription_period_end(plan_str)

        if event_type == "RENEWED":
            renewed = await renew_subscription_period(db, purchase_id, period_end)
            if renewed:
                return {"received": True}

        if user_id:
            if await payment_already_processed(db, purchase_id):
                logger.info("RuStore purchase %s already processed", purchase_id)
            else:
                plan = SubscriptionPlan.yearly if plan_str == "yearly" else SubscriptionPlan.monthly
                await activate_paid_subscription(
                    db,
                    UUID(str(user_id)),
                    plan,
                    purchase_id,
                    None,
                    period_end,
                    provider="rustore",
                    provider_payment_id=purchase_id,
                )
    elif parsed.get("canceled") and parsed.get("purchase_id"):
        # PAYMENT_FAILED / CANCELLED — отмена автопродления, доступ до end_date
        if event_type != "PAYMENT_FAILED":
            await cancel_subscription_record(db, str(parsed["purchase_id"]))

    return {"received": True}


@router.post("/tbank")
async def tbank_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Webhook Т-Банк: только с валидной подписью Token."""
    payload = await request.body()
    tb = TBankProvider()

    if not tb.is_available():
        raise HTTPException(503, "T-Bank is not configured")

    try:
        notification = tb.construct_webhook_event(payload)
    except Exception as e:
        logger.warning("T-Bank webhook error: %s", e)
        raise HTTPException(400, "Invalid webhook") from e

    result = await tb.handle_payment_confirmed(notification)

    # Активация только после CONFIRMED (не AUTHORIZED до списания)
    if (
        result.get("status") == "CONFIRMED"
        and result.get("user_id")
        and result.get("payment_id")
    ):
        payment_id = str(result["payment_id"])
        if await payment_already_processed(db, payment_id):
            logger.info("T-Bank payment %s already processed", payment_id)
        else:
            plan_str = result.get("plan", "monthly")
            plan = SubscriptionPlan.yearly if plan_str == "yearly" else SubscriptionPlan.monthly
            await activate_paid_subscription(
                db,
                UUID(str(result["user_id"])),
                plan,
                payment_id,
                None,
                subscription_period_end(plan_str),
                provider="tbank",
                provider_payment_id=payment_id,
            )
    elif result.get("status") in ("REJECTED", "CANCELED", "REVERSED") and result.get("payment_id"):
        if not await payment_already_processed(db, str(result["payment_id"])):
            await cancel_subscription_record(db, str(result["payment_id"]))

    return {"received": True}


@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Legacy webhook Stripe (при PAYMENT_PROVIDER=stripe)."""
    if settings.payment_provider.lower() != "stripe":
        raise HTTPException(404, "Stripe webhook disabled; use /webhook/yookassa")

    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    provider = StripePaymentProvider()

    try:
        event = provider.construct_webhook_event(payload, sig)
    except Exception as e:
        logger.warning("Webhook signature failed: %s", e)
        raise HTTPException(400, "Invalid signature") from e

    def _ts_to_dt(ts: int | None) -> datetime | None:
        if ts is None:
            return None
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    event_type = event.get("type", "")
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        metadata = data.get("metadata") or {}
        user_id = metadata.get("user_id")
        plan_str = metadata.get("plan", "monthly")
        sub_id = data.get("subscription")
        if user_id and sub_id:
            if await payment_already_processed(db, str(sub_id)):
                logger.info("Stripe subscription %s already processed", sub_id)
                return {"received": True}
            plan = SubscriptionPlan.yearly if plan_str == "yearly" else SubscriptionPlan.monthly
            # Не использовать expires_at сессии (~24ч) — только период плана
            period_end = subscription_period_end(plan_str)
            await activate_paid_subscription(
                db,
                UUID(user_id),
                plan,
                str(sub_id),
                data.get("customer"),
                period_end,
                provider="stripe",
                provider_payment_id=str(sub_id),
            )
    elif event_type in ("invoice.paid", "customer.subscription.updated"):
        sub_id = data.get("subscription") or data.get("id")
        period_end = _ts_to_dt(data.get("current_period_end"))
        if sub_id and period_end:
            await renew_subscription_period(db, str(sub_id), period_end)
    elif event_type == "customer.subscription.deleted":
        sub_id = data.get("id")
        if sub_id:
            await cancel_subscription_record(db, str(sub_id))

    return {"received": True}
