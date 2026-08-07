"""Тесты Т-Банк провайдера / T-Bank provider tests."""

import json
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.config import COUNTRY_PRICING, settings
from app.services.payment import MockPaymentProvider, get_payment_provider
from app.services.tbank_provider import (
    TBankPaymentProvider,
    TBankProvider,
    generate_tbank_token,
    verify_tbank_webhook,
)


def test_generate_tbank_token_deterministic():
    params = {"TerminalKey": "TKey", "Amount": 24900, "OrderId": "order1"}
    t1 = generate_tbank_token(params, "pass")
    t2 = generate_tbank_token(params, "pass")
    assert t1 == t2
    assert len(t1) == 64


def test_verify_tbank_webhook_valid():
    params = {
        "TerminalKey": "TKey",
        "Status": "CONFIRMED",
        "PaymentId": 12345,
        "OrderId": "he_order",
    }
    params["Token"] = generate_tbank_token(params, "secret")
    assert verify_tbank_webhook(params, "secret") is True


def test_verify_tbank_webhook_invalid():
    params = {"TerminalKey": "TKey", "Status": "CONFIRMED", "Token": "bad"}
    assert verify_tbank_webhook(params, "secret") is False


def test_tbank_provider_not_available_without_keys():
    tb = TBankProvider(terminal_key="", password="")
    assert tb.is_available() is False


def test_minor_units_from_country_pricing():
    tb = TBankProvider(terminal_key="TKey", password="pass")
    assert COUNTRY_PRICING["RU"]["monthly"] == 24900
    assert tb.is_available() is True


@pytest.mark.asyncio
async def test_create_checkout_session_mocked():
    tb = TBankProvider(terminal_key="TKey", password="secret")
    mock_resp = AsyncMock()
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: {"Success": True, "PaymentURL": "https://securepay.tinkoff.ru/pay/abc"}

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.tbank_provider.httpx.AsyncClient", return_value=mock_client):
        url = await tb.create_checkout_session(uuid4(), "u@test.com", "RU", "monthly")

    assert url == "https://securepay.tinkoff.ru/pay/abc"
    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args
    assert call_args[0][0].endswith("/Init")
    body = call_args[1]["json"]
    assert body["Amount"] == COUNTRY_PRICING["RU"]["monthly"]
    assert "Token" in body


def test_construct_webhook_event_valid_token():
    tb = TBankProvider(terminal_key="TKey", password="secret")
    notification = {
        "TerminalKey": "TKey",
        "Status": "CONFIRMED",
        "PaymentId": 999,
        "OrderId": "he_1",
        "DATA": {"user_id": str(uuid4()), "plan": "monthly"},
    }
    notification["Token"] = generate_tbank_token(notification, "secret")
    payload = json.dumps(notification).encode()
    parsed = tb.construct_webhook_event(payload)
    assert parsed["Status"] == "CONFIRMED"


def test_construct_webhook_event_invalid_token():
    tb = TBankProvider(terminal_key="TKey", password="secret")
    payload = json.dumps({"TerminalKey": "TKey", "Status": "CONFIRMED", "Token": "invalid"}).encode()
    with pytest.raises(ValueError, match="Invalid T-Bank webhook signature"):
        tb.construct_webhook_event(payload)


@pytest.mark.asyncio
async def test_handle_payment_confirmed():
    tb = TBankProvider(terminal_key="TKey", password="secret")
    uid = str(uuid4())
    result = await tb.handle_payment_confirmed(
        {
            "Status": "CONFIRMED",
            "PaymentId": 555,
            "OrderId": "he_x",
            "DATA": {"user_id": uid, "plan": "yearly"},
        }
    )
    assert result["confirmed"] is True
    assert result["user_id"] == uid
    assert result["plan"] == "yearly"
    assert result["payment_id"] == "555"


@pytest.mark.asyncio
async def test_get_payment_provider_tbank_configured(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "tbank")
    monkeypatch.setattr(settings, "tbank_terminal_key", "TKey")
    monkeypatch.setattr(settings, "tbank_password", "secret")
    assert isinstance(get_payment_provider(), TBankPaymentProvider)


@pytest.mark.asyncio
async def test_get_payment_provider_tbank_mock_fallback(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "tbank")
    monkeypatch.setattr(settings, "tbank_terminal_key", "")
    monkeypatch.setattr(settings, "tbank_password", "")
    assert isinstance(get_payment_provider(), MockPaymentProvider)


@pytest.mark.asyncio
async def test_tbank_payment_provider_adapter():
    adapter = TBankPaymentProvider()
    with patch.object(
        adapter._inner,
        "create_checkout_session",
        new_callable=AsyncMock,
        return_value="https://pay.url",
    ):
        url = await adapter.create_checkout_session(uuid4(), "a@b.com", "", "KZ", "monthly")
    assert url == "https://pay.url"
