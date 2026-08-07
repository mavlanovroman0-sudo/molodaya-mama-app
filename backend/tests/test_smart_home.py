"""Тесты умного дома / Smart home provider tests."""

import pytest

from app.services.smart_home.providers import (
    GoogleHomeProvider,
    HomeAssistantProvider,
    YandexSmartHomeProvider,
    get_provider,
)


@pytest.mark.asyncio
async def test_home_assistant_provider():
    p = HomeAssistantProvider("http://localhost:8123", "token")
    devices = await p.list_devices()
    assert len(devices) >= 1
    result = await p.send_command("light.kitchen", "turn_on", {})
    assert result["success"]


@pytest.mark.asyncio
async def test_yandex_provider():
    p = YandexSmartHomeProvider("oauth")
    state = await p.get_state("yandex:tea_kettle")
    assert "temperature" in state


@pytest.mark.asyncio
async def test_provider_factory():
    p = get_provider("google", {"project_id": "x", "credentials": {}})
    assert isinstance(p, GoogleHomeProvider)
