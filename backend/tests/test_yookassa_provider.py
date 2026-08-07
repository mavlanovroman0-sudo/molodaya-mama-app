"""Тесты YooKassa провайдера / YooKassa provider tests."""

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.config import COUNTRY_PRICING, settings
from app.services.payment import MockPaymentProvider, get_payment_provider
from app.services.yookassa_provider import (
    YooKassaPaymentProvider,
    YooKassaProvider,
    format_yookassa_amount,
    subscription_period_end,
)


def test_format_yookassa_amount_rub():
    assert format_yookassa_amount(24900, "rub") == "249.00"


def test_format_yookassa_amount_uzs_whole_units():
    assert format_yookassa_amount(24500, "uzs") == "24500.00"


def test_subscription_period_end():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end_m = subscription_period_end("monthly", start)
    end_y = subscription_period_end("yearly", start)
    assert (end_m - start).days == 30
    assert (end_y - start).days == 365


def test_yookassa_provider_not_available_without_keys():
    yk = YooKassaProvider(shop_id="", secret_key="")
    assert yk.is_available() is False


def test_construct_webhook_event():
    yk = YooKassaProvider(shop_id="123", secret_key="test_key")
    payload = json.dumps({"event": "payment.succeeded", "object": {"id": "pay_1"}}).encode()
    event = yk.construct_webhook_event(payload)
    assert event["event"] == "payment.succeeded"


@pytest.mark.asyncio
async def test_create_checkout_session_mocked():
    yk = YooKassaProvider(shop_id="123456", secret_key="test_abc")
    with patch.object(yk, "_ensure_configured"):
        with patch(
            "app.services.yookassa_provider.asyncio.to_thread",
            new_callable=AsyncMock,
            return_value="https://yookassa.ru/checkout/test",
        ):
            url = await yk.create_checkout_session(uuid4(), "u@test.com", "RU", "monthly")
    assert url == "https://yookassa.ru/checkout/test"


@pytest.mark.asyncio
async def test_get_payment_provider_yookassa_default(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "yookassa")
    monkeypatch.setattr(settings, "yookassa_shop_id", "")
    monkeypatch.setattr(settings, "yookassa_secret_key", "")
    assert isinstance(get_payment_provider(), MockPaymentProvider)


@pytest.mark.asyncio
async def test_get_payment_provider_yookassa_configured(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "yookassa")
    monkeypatch.setattr(settings, "yookassa_shop_id", "123456")
    monkeypatch.setattr(settings, "yookassa_secret_key", "test_secret_key_xyz")
    assert isinstance(get_payment_provider(), YooKassaPaymentProvider)


@pytest.mark.asyncio
async def test_yookassa_payment_provider_adapter():
    adapter = YooKassaPaymentProvider()
    with patch.object(
        adapter._inner,
        "create_checkout_session",
        new_callable=AsyncMock,
        return_value="https://pay.url",
    ):
        url = await adapter.create_checkout_session(uuid4(), "a@b.com", "", "RU", "yearly")
    assert url == "https://pay.url"


def test_country_pricing_unchanged():
    assert COUNTRY_PRICING["RU"]["monthly"] == 24900
    assert COUNTRY_PRICING["KZ"]["yearly"] == 1000000
