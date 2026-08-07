"""Бизнес-логика подписки / Subscription service."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import COUNTRY_PRICING, settings
from app.models import User
from app.models_subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from app.services.payment import get_available_payment_providers, get_client_payment_providers


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def get_latest_subscription(db: AsyncSession, user_id: UUID) -> Subscription | None:
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id)
        .order_by(Subscription.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


def _is_subscription_active(sub: Subscription | None, now: datetime | None = None) -> bool:
    """Доступ есть при active/trialing, а также при canceled до конца оплаченного периода."""
    if not sub:
        return False
    now = now or _now()
    if sub.status == SubscriptionStatus.trialing:
        end = sub.trial_end or sub.end_date
        return bool(end and end > now)
    if sub.status in (SubscriptionStatus.active, SubscriptionStatus.canceled):
        return bool(sub.end_date and sub.end_date > now)
    return False


async def user_has_access(db: AsyncSession, user_id: UUID) -> bool:
    if not settings.subscription_enforce:
        return True
    sub = await get_latest_subscription(db, user_id)
    return _is_subscription_active(sub)


async def start_trial(db: AsyncSession, user: User) -> Subscription:
    """Запуск 14-дневного пробного периода при регистрации."""
    now = _now()
    trial_end = now + timedelta(days=settings.trial_days)
    sub = Subscription(
        user_id=user.id,
        status=SubscriptionStatus.trialing,
        plan=SubscriptionPlan.trial,
        start_date=now,
        trial_start=now,
        trial_end=trial_end,
        end_date=trial_end,
        provider="internal",
    )
    user.trial_used = True
    db.add(sub)
    await db.flush()
    return sub


def _days_remaining(end: datetime | None) -> int:
    if not end:
        return 0
    delta = end - _now()
    return max(0, delta.days)


def get_pricing_for_country(country_code: str) -> dict:
    return COUNTRY_PRICING.get(country_code.upper(), COUNTRY_PRICING["RU"])


async def build_subscription_prices(
    user: User,
    *,
    client_ip: str | None = None,
) -> dict:
    """Цены по геолокации пользователя + полный прайс-лист по странам."""
    from app.services.geo import detect_location

    geo = await detect_location(
        ip=client_ip,
        latitude=float(user.latitude) if user.latitude is not None else None,
        longitude=float(user.longitude) if user.longitude is not None else None,
    )
    country_code = geo.country_code or user.country_code or "RU"
    pricing = get_pricing_for_country(country_code)

    return {
        "country_code": country_code,
        "currency": pricing["currency"],
        "monthly": pricing["monthly_display"],
        "yearly": pricing["yearly_display"],
        "monthly_amount": pricing["monthly"],
        "yearly_amount": pricing["yearly"],
        "vat_included": True,
        "country_pricing": COUNTRY_PRICING,
        "available_providers": get_client_payment_providers(),
    }


async def build_subscription_status(db: AsyncSession, user: User) -> dict:
    sub = await get_latest_subscription(db, user.id)
    now = _now()
    has_access = _is_subscription_active(sub, now)
    pricing = get_pricing_for_country(user.country_code or "RU")

    status = SubscriptionStatus.expired.value
    plan = None
    days_remaining = 0
    trial_end = None
    end_date = None

    if sub:
        status = sub.status.value
        plan = sub.plan.value
        if sub.status == SubscriptionStatus.trialing and sub.trial_end:
            trial_end = sub.trial_end.isoformat()
            days_remaining = _days_remaining(sub.trial_end)
            end_date = sub.trial_end.isoformat()
        elif sub.end_date:
            end_date = sub.end_date.isoformat()
            days_remaining = _days_remaining(sub.end_date)

    can_cancel = bool(
        sub
        and sub.status == SubscriptionStatus.active
        and sub.plan != SubscriptionPlan.trial
        and sub.provider_subscription_id
        and sub.provider not in ("internal", "")
    )

    return {
        "status": status,
        "plan": plan,
        "has_access": has_access,
        "days_remaining": days_remaining,
        "trial_end": trial_end,
        "end_date": end_date,
        "country_code": user.country_code or "RU",
        "trial_used": user.trial_used,
        "trial_days": settings.trial_days,
        "pricing": {
            "monthly": pricing["monthly_display"],
            "yearly": pricing["yearly_display"],
            "currency": pricing["currency"],
        },
        "available_providers": get_client_payment_providers(),
        "can_cancel": can_cancel,
        "current_provider": sub.provider if sub and sub.provider not in ("internal", "") else None,
        "vat_included": True,
    }


async def activate_paid_subscription(
    db: AsyncSession,
    user_id: UUID,
    plan: SubscriptionPlan,
    provider_subscription_id: str,
    provider_customer_id: str | None,
    period_end: datetime,
    provider: str = "yookassa",
    provider_payment_id: str | None = None,
    yookassa_payment_method_id: str | None = None,
) -> Subscription:
    sub = await get_latest_subscription(db, user_id)
    now = _now()
    if sub:
        sub.status = SubscriptionStatus.active
        sub.plan = plan
        sub.end_date = period_end
        sub.provider = provider
        sub.provider_subscription_id = provider_subscription_id
        sub.provider_payment_id = provider_payment_id or provider_subscription_id
        sub.provider_customer_id = provider_customer_id
        if yookassa_payment_method_id:
            sub.yookassa_payment_method_id = yookassa_payment_method_id
        sub.trial_end = None
    else:
        sub = Subscription(
            user_id=user_id,
            status=SubscriptionStatus.active,
            plan=plan,
            start_date=now,
            end_date=period_end,
            provider=provider,
            provider_subscription_id=provider_subscription_id,
            provider_payment_id=provider_payment_id or provider_subscription_id,
            provider_customer_id=provider_customer_id,
            yookassa_payment_method_id=yookassa_payment_method_id,
        )
        db.add(sub)
    await db.flush()
    return sub


async def cancel_subscription_record(db: AsyncSession, provider_subscription_id: str) -> None:
    """Отмена автопродления: статус canceled, доступ сохраняется до end_date."""
    result = await db.execute(
        select(Subscription).where(Subscription.provider_subscription_id == provider_subscription_id)
    )
    sub = result.scalar_one_or_none()
    if sub and sub.status != SubscriptionStatus.expired:
        sub.status = SubscriptionStatus.canceled
        await db.flush()


async def renew_subscription_period(
    db: AsyncSession,
    provider_payment_id: str,
    period_end: datetime,
) -> Subscription | None:
    """Продление периода при RENEWED (тот же purchase/payment id)."""
    result = await db.execute(
        select(Subscription).where(Subscription.provider_payment_id == provider_payment_id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        return None
    sub.status = SubscriptionStatus.active
    if not sub.end_date or period_end > sub.end_date:
        sub.end_date = period_end
    await db.flush()
    return sub


async def payment_already_processed(db: AsyncSession, provider_payment_id: str) -> bool:
    """Idempotency: подписка с этим provider_payment_id уже активирована."""
    if not provider_payment_id:
        return False
    result = await db.execute(
        select(Subscription).where(
            Subscription.provider_payment_id == provider_payment_id,
            Subscription.status.in_(
                (SubscriptionStatus.active, SubscriptionStatus.canceled)
            ),
        )
    )
    return result.scalar_one_or_none() is not None


async def expire_subscription(db: AsyncSession, user_id: UUID) -> None:
    sub = await get_latest_subscription(db, user_id)
    if sub:
        sub.status = SubscriptionStatus.expired
        await db.flush()


async def expire_due_subscriptions(db: AsyncSession) -> int:
    """Перевести в expired все подписки с истёкшим end_date/trial_end."""
    now = _now()
    result = await db.execute(
        select(Subscription).where(
            Subscription.status.in_(
                (
                    SubscriptionStatus.active,
                    SubscriptionStatus.trialing,
                    SubscriptionStatus.canceled,
                )
            )
        )
    )
    count = 0
    for sub in result.scalars().all():
        end = sub.trial_end if sub.status == SubscriptionStatus.trialing else sub.end_date
        if end and end <= now:
            sub.status = SubscriptionStatus.expired
            count += 1
    if count:
        await db.flush()
    return count
