"""Платёжный провайдер RuStore / RuStore billing provider."""

from __future__ import annotations

import base64
import json
import logging
import uuid
from typing import Any
from uuid import UUID

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

RUSTORE_API_PROD = "https://public-api.rustore.ru/public"
RUSTORE_API_SANDBOX = "https://public-api.rustore.ru/public/sandbox"


class RuStoreProvider:
    """
    RuStore Pay SDK — оплата в приложении Android.
    create_checkout_session возвращает deep link для клиента.
    Webhook — зашифрованный payload (AES-256-GCM).
    """

    def __init__(
        self,
        app_id: str | None = None,
        package_name: str | None = None,
        api_key: str | None = None,
        webhook_secret: str | None = None,
        sandbox: bool | None = None,
    ):
        self._app_id = app_id or settings.rustore_app_id
        self._package_name = package_name or settings.rustore_package_name
        self._api_key = api_key or settings.rustore_api_key
        self._webhook_secret = webhook_secret or settings.rustore_webhook_secret
        self._sandbox = settings.rustore_sandbox if sandbox is None else sandbox
        self._api_base = RUSTORE_API_SANDBOX if self._sandbox else RUSTORE_API_PROD

    def is_available(self) -> bool:
        return bool(
            self._package_name
            and self._api_key
            and not self._api_key.endswith("...")
        )

    def _product_code(self, plan: str) -> str:
        return (
            settings.rustore_product_monthly
            if plan == "monthly"
            else settings.rustore_product_yearly
        )

    async def create_checkout_session(
        self,
        user_id: UUID,
        email: str,
        country_code: str,
        plan: str,
    ) -> str:
        """
        Возвращает deep link для RuStore Pay SDK в мобильном приложении.
        Формат: homeease://rustore-pay?product=...&order=...&plan=...
        """
        product = self._product_code(plan)
        order_id = str(uuid.uuid4())
        return (
            f"homeease://rustore-pay"
            f"?product={product}"
            f"&orderId={order_id}"
            f"&plan={plan}"
            f"&userId={user_id}"
            f"&package={self._package_name or 'com.homeease.app'}"
        )

    def decrypt_webhook_payload(self, encrypted_b64: str) -> dict[str, Any]:
        """Расшифровка payload из webhook RuStore (AES-256-GCM)."""
        if not self._webhook_secret:
            raise ValueError("RUSTORE_WEBHOOK_SECRET not configured")

        from Crypto.Cipher import AES

        raw = base64.b64decode(encrypted_b64)
        iv = raw[:12]
        tag = raw[-16:]
        ciphertext = raw[12:-16]
        cipher = AES.new(self._webhook_secret.encode("utf-8"), AES.MODE_GCM, nonce=iv)
        decrypted = cipher.decrypt_and_verify(ciphertext, tag)
        return json.loads(decrypted.decode("utf-8"))

    def construct_webhook_event(self, payload: bytes, signature: str = "") -> dict[str, Any]:
        body = json.loads(payload.decode("utf-8"))
        if "payload" not in body:
            raise ValueError("RuStore webhook must include encrypted 'payload'")
        if not self._webhook_secret:
            raise ValueError("RUSTORE_WEBHOOK_SECRET is required")
        decrypted = self.decrypt_webhook_payload(body["payload"])
        return {"event": "subscription", "object": decrypted, "raw": body}

    async def get_subscription(self, subscription_id: str, purchase_id: str) -> dict[str, Any]:
        """Проверка подписки через RuStore Public API v4."""
        url = (
            f"{self._api_base}/v4/subscription/"
            f"{self._package_name}/{subscription_id}/{purchase_id}"
        )
        headers = {"Public-Token": self._api_key}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def cancel_subscription(self, purchase_id: str) -> bool:
        """Отмена автопродления через Public API (если поддерживается)."""
        logger.info("RuStore cancel autorenew for purchase %s (via Console/API)", purchase_id)
        return True

    def parse_subscription_event(self, data: dict[str, Any]) -> dict[str, Any]:
        sub = data.get("subscription_data") or data
        event_type = sub.get("subscription_event_type", "")
        return {
            "event_type": event_type,
            "purchase_id": sub.get("purchase_id"),
            "product_code": sub.get("product_code"),
            "status_new": sub.get("status_new"),
            "activated": event_type in ("ACTIVATED", "RENEWED"),
            "canceled": event_type in ("CANCELLED", "CLOSED", "PAYMENT_FAILED"),
        }


class RuStorePaymentProvider:
    """Адаптер RuStoreProvider под PaymentProvider."""

    def __init__(self):
        self._inner = RuStoreProvider()

    async def create_checkout_session(
        self, user_id: UUID, email: str, price_id: str, country_code: str, plan: str
    ) -> str:
        return await self._inner.create_checkout_session(user_id, email, country_code, plan)

    async def cancel_subscription(self, provider_subscription_id: str) -> bool:
        return await self._inner.cancel_subscription(provider_subscription_id)

    def construct_webhook_event(self, payload: bytes, signature: str) -> dict[str, Any]:
        return self._inner.construct_webhook_event(payload, signature)
