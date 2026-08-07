"""Тесты подписки и платежей / Subscription & payment tests."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.config import settings
from app.models_subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from app.services.payment import MockPaymentProvider, StripePaymentProvider, get_payment_provider
from app.services.rustore_provider import RuStorePaymentProvider
from app.services.tbank_provider import TBankPaymentProvider
from app.services.subscription import _is_subscription_active, get_pricing_for_country


def test_get_available_payment_providers_empty(monkeypatch):
    monkeypatch.setattr("app.services.payment.settings.yookassa_shop_id", "")
    monkeypatch.setattr("app.services.payment.settings.yookassa_secret_key", "")
    monkeypatch.setattr("app.services.payment.settings.rustore_package_name", "")
    monkeypatch.setattr("app.services.payment.settings.rustore_api_key", "")
    monkeypatch.setattr("app.services.payment.settings.tbank_terminal_key", "")
    monkeypatch.setattr("app.services.payment.settings.tbank_password", "")
    from app.services.payment import get_available_payment_providers

    assert get_available_payment_providers() == []


def test_get_available_payment_providers_yookassa(monkeypatch):
    monkeypatch.setattr("app.services.payment.settings.yookassa_shop_id", "shop")
    monkeypatch.setattr("app.services.payment.settings.yookassa_secret_key", "secret")
    from app.services.payment import get_available_payment_providers

    ids = [p["id"] for p in get_available_payment_providers()]
    assert "yookassa" in ids


def test_pricing_by_country():
    ru = get_pricing_for_country("RU")
    assert ru["monthly_display"] == "249 ₽"
    assert ru["yearly_display"] == "1990 ₽"
    kz = get_pricing_for_country("KZ")
    assert "1250" in kz["monthly_display"]


def test_is_subscription_active_trial():
    now = datetime.now(timezone.utc)
    sub = Subscription(
        user_id=uuid4(),
        status=SubscriptionStatus.trialing,
        plan=SubscriptionPlan.trial,
        trial_end=now + timedelta(days=5),
        end_date=now + timedelta(days=5),
    )
    assert _is_subscription_active(sub, now) is True

    sub.trial_end = now - timedelta(days=1)
    assert _is_subscription_active(sub, now) is False


def test_is_subscription_active_canceled_until_period_end():
    now = datetime.now(timezone.utc)
    sub = Subscription(
        user_id=uuid4(),
        status=SubscriptionStatus.canceled,
        plan=SubscriptionPlan.monthly,
        end_date=now + timedelta(days=10),
    )
    assert _is_subscription_active(sub, now) is True
    sub.end_date = now - timedelta(days=1)
    assert _is_subscription_active(sub, now) is False


@pytest.mark.asyncio(loop_scope="session")
async def test_mock_payment_provider_checkout():
    provider = MockPaymentProvider()
    url = await provider.create_checkout_session(uuid4(), "a@b.com", "price_x", "RU", "monthly")
    assert "mock" in url or "yookassa" in url


def test_mock_payment_webhook():
    provider = MockPaymentProvider()
    event = provider.construct_webhook_event(
        b'{"type": "checkout.session.completed", "data": {}}', "sig"
    )
    assert event["type"] == "checkout.session.completed"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_payment_provider_mock_without_key(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "yookassa")
    monkeypatch.setattr(settings, "yookassa_shop_id", "")
    monkeypatch.setattr(settings, "yookassa_secret_key", "")
    assert isinstance(get_payment_provider(), MockPaymentProvider)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_payment_provider_stripe(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "stripe")
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_fake")
    assert isinstance(get_payment_provider(), StripePaymentProvider)


@pytest.mark.asyncio(loop_scope="session")
async def test_stripe_provider_create_session_mocked(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "stripe")
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_fake")

    mock_stripe = MagicMock()
    mock_stripe.checkout.Session.create.return_value = MagicMock(url="https://stripe.com/pay")

    provider = StripePaymentProvider("sk_test_fake")
    with patch.object(provider, "_client", return_value=mock_stripe):
        url = await provider.create_checkout_session(uuid4(), "u@t.com", "price_1", "RU", "monthly")
    assert url == "https://stripe.com/pay"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_payment_provider_rustore(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "rustore")
    monkeypatch.setattr(settings, "rustore_package_name", "com.homeease.app")
    monkeypatch.setattr(settings, "rustore_api_key", "public_token")
    assert isinstance(get_payment_provider(), RuStorePaymentProvider)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_payment_provider_tbank(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "tbank")
    monkeypatch.setattr(settings, "tbank_terminal_key", "TKey")
    monkeypatch.setattr(settings, "tbank_password", "secret")
    assert isinstance(get_payment_provider(), TBankPaymentProvider)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_payment_provider_by_name_override(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "yookassa")
    monkeypatch.setattr(settings, "tbank_terminal_key", "TKey")
    monkeypatch.setattr(settings, "tbank_password", "secret")
    assert isinstance(get_payment_provider("tbank"), TBankPaymentProvider)


@pytest.mark.asyncio(loop_scope="session")
async def test_build_subscription_prices_uses_country():
    from app.models import User
    from app.services.subscription import build_subscription_prices

    user = User(email="t@t.com", country_code="KZ")
    data = await build_subscription_prices(user, client_ip="127.0.0.1")
    assert data["country_code"] == "RU"  # localhost defaults to RU geo
    assert data["currency"] == "rub"
    assert "249 ₽" in data["monthly"]
    assert "RU" in data["country_pricing"]
    assert data["vat_included"] is True

