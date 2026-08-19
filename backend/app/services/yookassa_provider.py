"""Платёжный провайдер YooKassa / YooKassa payment provider."""

from __future__ import annotations

import asyncio
import json
import logging
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from app.config import COUNTRY_PRICING, settings
from app.services.subscription import activate_paid_subscription, cancel_subscription_record

logger = logging.getLogger(__name__)

# Валюты, где сумма в COUNTRY_PRICING уже в целых единицах (без деления на 100)
_WHOLE_UNIT_CURRENCIES = frozenset({"uzs"})


def _yookassa_currency(code: str) -> str:
    return code.upper()


_RECEIPT_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_receipt_email(email: str | None) -> str:
    value = (email or "").strip()
    return value if _RECEIPT_EMAIL.match(value) else ""


def format_yookassa_amount(amount_minor: int, currency: str) -> str:
    """Конвертация суммы из COUNTRY_PRICING в строку для YooKassa API."""
    cur = currency.lower()
    if cur in _WHOLE_UNIT_CURRENCIES:
        return f"{amount_minor:.2f}"
    return f"{amount_minor / 100:.2f}"


def build_yookassa_receipt(
    email: str,
    plan: str,
    amount_value: str,
    currency: str,
    vat_code: int = 1,
    phone: str | None = None,
) -> dict[str, Any]:
    """Чек 54-ФЗ: боевой магазин ЮKassa без него отклоняет платёж."""
    period = "год" if plan == "yearly" else "месяц"
    customer: dict[str, str] = {"email": email}
    phone_norm = (phone or "").strip()
    if phone_norm:
        customer["phone"] = phone_norm
    return {
        "customer": customer,
        "email": email,
        "items": [
            {
                "description": f"Подписка молодая мама, {period}",
                "quantity": 1.0,
                "amount": {"value": amount_value, "currency": currency},
                "vat_code": vat_code,
                "payment_mode": "full_payment",
                "payment_subject": "service",
            }
        ],
    }


def _yookassa_error_message(exc: BaseException) -> str:
    args = getattr(exc, "args", ())
    if args and isinstance(args[0], dict):
        return str(args[0].get("description") or args[0])
    return str(exc)


def subscription_period_end(plan: str, start: datetime | None = None) -> datetime:
    start = start or datetime.now(timezone.utc)
    days = 365 if plan == "yearly" else 30
    return start + timedelta(days=days)


class YooKassaProvider:
    """Интеграция с YooKassa API (разовые платежи за период подписки)."""

    def __init__(self, shop_id: str | None = None, secret_key: str | None = None):
        self._shop_id = shop_id or settings.yookassa_shop_id
        self._secret_key = secret_key or settings.yookassa_secret_key
        self._configured = False

    def _ensure_configured(self) -> None:
        if self._configured:
            return
        from yookassa import Configuration

        Configuration.account_id = self._shop_id
        Configuration.secret_key = self._secret_key
        self._configured = True

    def is_available(self) -> bool:
        return bool(
            self._shop_id
            and self._secret_key
            and not self._shop_id.endswith("...")
            and not self._secret_key.endswith("...")
        )

    def _pricing(self, country_code: str, plan: str) -> dict:
        pricing = COUNTRY_PRICING.get(country_code.upper(), COUNTRY_PRICING["RU"])
        if plan not in ("monthly", "yearly"):
            raise ValueError("plan must be monthly or yearly")
        return pricing

    async def create_checkout_session(
        self,
        user_id: UUID,
        email: str,
        country_code: str,
        plan: str,
        success_url: str | None = None,
        cancel_url: str | None = None,
    ) -> str:
        """Создаёт платёж в YooKassa и возвращает confirmation_url."""
        self._ensure_configured()
        pricing = self._pricing(country_code, plan)
        amount_value = format_yookassa_amount(pricing[plan], pricing["currency"])
        currency = _yookassa_currency(pricing["currency"])
        return_url = success_url or settings.payment_success_url

        email_norm = normalize_receipt_email(email)
        if not email_norm:
            raise RuntimeError(
                "В аккаунте нет почты для чека. Выйдите и войдите снова по электронной почте."
            )

        def _create() -> str:
            import requests
            from requests.auth import HTTPBasicAuth

            payload = {
                "amount": {"value": amount_value, "currency": currency},
                "confirmation": {"type": "redirect", "return_url": return_url},
                "capture": True,
                "description": f"молодая мама ({plan}, {country_code})",
                "receipt": build_yookassa_receipt(
                    email_norm, plan, amount_value, currency
                ),
                "metadata": {
                    "user_id": str(user_id),
                    "plan": plan,
                    "country_code": country_code.upper(),
                    "email": email_norm,
                },
            }
            try:
                response = requests.post(
                    "https://api.yookassa.ru/v3/payments",
                    auth=HTTPBasicAuth(str(self._shop_id), str(self._secret_key)),
                    headers={
                        "Idempotence-Key": str(uuid.uuid4()),
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30,
                )
                data = response.json() if response.content else {}
            except Exception as exc:
                raise RuntimeError(f"YooKassa: {_yookassa_error_message(exc)}") from exc
            if response.status_code >= 400:
                raise RuntimeError(
                    f"YooKassa: {data.get('description') or data or response.status_code}"
                )
            url = (data.get("confirmation") or {}).get("confirmation_url")
            if not url:
                raise RuntimeError("YooKassa не вернула confirmation_url")
            return url

        return await asyncio.to_thread(_create)

    def construct_webhook_event(self, payload: bytes, signature: str = "") -> dict[str, Any]:
        """
        Парсит webhook YooKassa.
        Подпись не используется — рекомендуется верифицировать платёж через API (см. handle_webhook).
        """
        try:
            data = json.loads(payload.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON payload") from e
        return data

    async def verify_payment(self, payment_id: str) -> dict[str, Any]:
        """Получает актуальный статус платежа из API YooKassa."""
        self._ensure_configured()

        def _find() -> dict:
            from yookassa import Payment

            payment = Payment.find_one(payment_id)
            if hasattr(payment, "json"):
                return json.loads(payment.json())
            return dict(payment)

        return await asyncio.to_thread(_find)

    async def handle_webhook(self, payload: bytes, signature: str = "") -> dict[str, Any]:
        """
        Обрабатывает уведомление YooKassa.
        Возвращает нормализованный результат для роутера.
        """
        event = self.construct_webhook_event(payload, signature)
        event_name = event.get("event", "")
        obj = event.get("object") or {}
        payment_id = obj.get("id")

        if payment_id and event_name.startswith("payment."):
            verified = await self.verify_payment(payment_id)
            obj = verified
            event_name = f"payment.{verified.get('status', 'unknown')}"

        return {
            "event": event_name,
            "object": obj,
            "raw": event,
        }

    async def activate_subscription(
        self,
        db,
        user_id: UUID,
        plan: str,
        provider_payment_id: str,
        customer_id: str | None = None,
    ):
        """Активирует подписку после успешной оплаты."""
        from app.models_subscription import SubscriptionPlan

        sub_plan = SubscriptionPlan.yearly if plan == "yearly" else SubscriptionPlan.monthly
        period_end = subscription_period_end(plan)
        return await activate_paid_subscription(
            db,
            user_id,
            sub_plan,
            provider_payment_id,
            customer_id,
            period_end,
            provider="yookassa",
        )

    async def cancel_subscription(self, provider_payment_id: str) -> bool:
        """
        YooKassa не поддерживает рекуррентные подписки через API.
        Отмена — только на стороне БД; незавершённый платёж можно отменить.
        """
        self._ensure_configured()

        def _cancel() -> bool:
            from yookassa import Payment

            try:
                payment = Payment.find_one(provider_payment_id)
                status = payment.status if hasattr(payment, "status") else payment.get("status")
                if status == "waiting_for_capture":
                    Payment.cancel(provider_payment_id, uuid.uuid4())
                return True
            except Exception as e:
                logger.warning("YooKassa cancel payment failed: %s", e)
                return False

        return await asyncio.to_thread(_cancel)


class YooKassaPaymentProvider:
    """Адаптер YooKassaProvider под интерфейс PaymentProvider."""

    def __init__(self):
        self._inner = YooKassaProvider()

    async def create_checkout_session(
        self,
        user_id: UUID,
        email: str,
        price_id: str,
        country_code: str,
        plan: str,
    ) -> str:
        return await self._inner.create_checkout_session(
            user_id, email, country_code, plan
        )

    async def cancel_subscription(self, provider_subscription_id: str) -> bool:
        return await self._inner.cancel_subscription(provider_subscription_id)

    def construct_webhook_event(self, payload: bytes, signature: str) -> dict[str, Any]:
        return self._inner.construct_webhook_event(payload, signature)
