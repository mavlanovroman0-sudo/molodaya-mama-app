"""Тесты RuStore провайдера / RuStore provider tests."""

import base64
import json
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from Crypto.Cipher import AES

from app.config import settings
from app.services.payment import MockPaymentProvider, get_payment_provider
from app.services.rustore_provider import RuStorePaymentProvider, RuStoreProvider


def _encrypt_payload(secret: str, data: dict) -> str:
    iv = b"\x00" * 12
    cipher = AES.new(secret.encode("utf-8"), AES.MODE_GCM, nonce=iv)
    ciphertext, tag = cipher.encrypt_and_digest(json.dumps(data).encode("utf-8"))
    return base64.b64encode(iv + ciphertext + tag).decode("ascii")


def test_rustore_provider_not_available_without_keys():
    rs = RuStoreProvider(package_name="", api_key="")
    assert rs.is_available() is False


def test_rustore_provider_available_with_keys():
    rs = RuStoreProvider(package_name="com.homeease.app", api_key="public_token_xyz")
    assert rs.is_available() is True


@pytest.mark.asyncio
async def test_create_checkout_session_returns_deep_link():
    rs = RuStoreProvider(package_name="com.homeease.app", api_key="key")
    uid = uuid4()
    url = await rs.create_checkout_session(uid, "u@test.com", "RU", "monthly")
    assert url.startswith("homeease://rustore-pay")
    assert "product=homeease_monthly" in url
    assert f"userId={uid}" in url


def test_parse_subscription_event_activated():
    rs = RuStoreProvider()
    parsed = rs.parse_subscription_event(
        {"subscription_event_type": "ACTIVATED", "purchase_id": "p1", "product_code": "homeease_monthly"}
    )
    assert parsed["activated"] is True
    assert parsed["purchase_id"] == "p1"


def test_construct_webhook_event_plain_json_rejected():
    rs = RuStoreProvider(package_name="com.app", api_key="k")
    payload = json.dumps({"subscription_event_type": "ACTIVATED", "purchase_id": "p2"}).encode()
    with pytest.raises(ValueError, match="encrypted"):
        rs.construct_webhook_event(payload)


def test_construct_webhook_event_encrypted():
    secret = "a" * 32
    rs = RuStoreProvider(package_name="com.app", api_key="k", webhook_secret=secret)
    inner = {"subscription_event_type": "RENEWED", "purchase_id": "p3", "product_code": "homeease_yearly"}
    encrypted = _encrypt_payload(secret, inner)
    payload = json.dumps({"payload": encrypted}).encode()
    event = rs.construct_webhook_event(payload)
    assert event["object"]["purchase_id"] == "p3"


@pytest.mark.asyncio
async def test_get_subscription_mocked():
    rs = RuStoreProvider(package_name="com.app", api_key="token")
    mock_resp = AsyncMock()
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: {"status": "ACTIVE"}

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.rustore_provider.httpx.AsyncClient", return_value=mock_client):
        data = await rs.get_subscription("sub_1", "purchase_1")

    assert data["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_get_payment_provider_rustore_configured(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "rustore")
    monkeypatch.setattr(settings, "rustore_package_name", "com.homeease.app")
    monkeypatch.setattr(settings, "rustore_api_key", "public_token")
    assert isinstance(get_payment_provider(), RuStorePaymentProvider)


@pytest.mark.asyncio
async def test_get_payment_provider_rustore_mock_fallback(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "rustore")
    monkeypatch.setattr(settings, "rustore_package_name", "")
    monkeypatch.setattr(settings, "rustore_api_key", "")
    assert isinstance(get_payment_provider(), MockPaymentProvider)


@pytest.mark.asyncio
async def test_rustore_payment_provider_adapter():
    adapter = RuStorePaymentProvider()
    with patch.object(
        adapter._inner,
        "create_checkout_session",
        new_callable=AsyncMock,
        return_value="homeease://rustore-pay?product=x",
    ):
        url = await adapter.create_checkout_session(uuid4(), "a@b.com", "", "RU", "yearly")
    assert url.startswith("homeease://")
