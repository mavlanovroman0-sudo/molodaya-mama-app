"""Платёжный провайдер Т-Банк (Tinkoff Acquiring) / T-Bank payment provider."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from typing import Any
from uuid import UUID

import httpx

from app.config import COUNTRY_PRICING, settings
from app.services.yookassa_provider import format_yookassa_amount, subscription_period_end

logger = logging.getLogger(__name__)


def _minor_units(country_code: str, plan: str) -> int:
    pricing = COUNTRY_PRICING.get(country_code.upper(), COUNTRY_PRICING["RU"])
    return int(pricing[plan])


def generate_tbank_token(params: dict[str, Any], password: str) -> str:
    """Генерация Token для запросов T-Bank API."""
    flat: dict[str, str] = {}
    for key, value in params.items():
        if key == "Token" or value is None:
            continue
        if isinstance(value, (dict, list)):
            continue
        flat[key] = str(value)
    flat["Password"] = password
    concat = "".join(flat[k] for k in sorted(flat.keys()))
    return hashlib.sha256(concat.encode("utf-8")).hexdigest()


def verify_tbank_webhook(payload: dict[str, Any], password: str) -> bool:
    import hmac

    token = payload.get("Token")
    if not token:
        return False
    expected = generate_tbank_token(dict(payload), password)
    return hmac.compare_digest(str(token), expected)


class TBankProvider:
    """Интеграция с API интернет-эквайринга Т-Банка."""

    def __init__(
        self,
        terminal_key: str | None = None,
        password: str | None = None,
        api_url: str | None = None,
    ):
        self._terminal_key = terminal_key or settings.tbank_terminal_key
        self._password = password or settings.tbank_password
        self._api_url = (api_url or settings.tbank_api_url).rstrip("/")

    def is_available(self) -> bool:
        return bool(
            self._terminal_key
            and self._password
            and not self._terminal_key.endswith("...")
            and not self._password.endswith("...")
        )

    async def _post(self, method: str, body: dict[str, Any]) -> dict[str, Any]:
        body["TerminalKey"] = self._terminal_key
        body["Token"] = generate_tbank_token(body, self._password)
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self._api_url}/{method}", json=body)
            resp.raise_for_status()
            data = resp.json()
        if not data.get("Success"):
            raise RuntimeError(data.get("Message", "T-Bank API error"))
        return data

    async def create_checkout_session(
        self,
        user_id: UUID,
        email: str,
        country_code: str,
        plan: str,
    ) -> str:
        amount = _minor_units(country_code, plan)
        order_id = f"he_{user_id.hex[:12]}_{uuid.uuid4().hex[:8]}"
        body: dict[str, Any] = {
            "Amount": amount,
            "OrderId": order_id,
            "Description": f"HomeEase Premium ({plan})",
            "SuccessURL": settings.payment_success_url,
            "FailURL": settings.payment_cancel_url,
            "DATA": {
                "user_id": str(user_id),
                "plan": plan,
                "country_code": country_code.upper(),
                "email": email,
            },
        }
        data = await self._post("Init", body)
        url = data.get("PaymentURL")
        if not url:
            raise RuntimeError("T-Bank не вернул PaymentURL")
        return url

    async def cancel_subscription(self, payment_id: str) -> bool:
        try:
            await self._post("Cancel", {"PaymentId": payment_id})
            return True
        except Exception as e:
            logger.warning("T-Bank cancel failed: %s", e)
            return False

    def construct_webhook_event(self, payload: bytes, signature: str = "") -> dict[str, Any]:
        data = json.loads(payload.decode("utf-8"))
        if self.is_available() and not verify_tbank_webhook(data, self._password):
            raise ValueError("Invalid T-Bank webhook signature")
        return data

    async def handle_payment_confirmed(self, notification: dict[str, Any]) -> dict[str, Any]:
        status = notification.get("Status", "")
        metadata = notification.get("DATA") or {}
        return {
            "status": status,
            "payment_id": str(notification.get("PaymentId", "")),
            "order_id": notification.get("OrderId"),
            "user_id": metadata.get("user_id"),
            "plan": metadata.get("plan", "monthly"),
            "confirmed": status == "CONFIRMED",
        }


class TBankPaymentProvider:
    """Адаптер TBankProvider под PaymentProvider."""

    def __init__(self):
        self._inner = TBankProvider()

    async def create_checkout_session(
        self, user_id: UUID, email: str, price_id: str, country_code: str, plan: str
    ) -> str:
        return await self._inner.create_checkout_session(user_id, email, country_code, plan)

    async def cancel_subscription(self, provider_subscription_id: str) -> bool:
        return await self._inner.cancel_subscription(provider_subscription_id)

    def construct_webhook_event(self, payload: bytes, signature: str) -> dict[str, Any]:
        return self._inner.construct_webhook_event(payload, signature)
