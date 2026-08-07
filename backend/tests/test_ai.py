"""Тесты AI заглушек / AI stub tests."""

import pytest

from app.services.ai import predict_price, substitute_ingredient, predict_sleep_phase


@pytest.mark.asyncio
async def test_price_prediction_stub():
    result = await predict_price("молоко", "Центральный", "ru")
    assert "current_price" in result
    assert "predicted_low" in result
    assert result["product"] == "молоко"


@pytest.mark.asyncio
async def test_ingredient_substitute_stub():
    result = await substitute_ingredient("crème fraîche", "Москва", "ru")
    assert "substitutes" in result
    assert len(result["substitutes"]) > 0


@pytest.mark.asyncio
async def test_sleep_phase_stub():
    result = await predict_sleep_phase(4, [{"start": "2025-01-01T10:00:00"}], "ru")
    assert result["current_phase"] in ("light", "deep", "rem", "awake")
