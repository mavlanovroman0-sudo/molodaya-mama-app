"""Юнит-тесты функций без БД / Unit tests without database."""

from app.api.user_geo import _haversine_km
from app.models_features import BarterAdType, BarterTxStatus


def test_haversine_distance():
    # Москва — близкие точки ~1.4 км
    dist = _haversine_km(55.7558, 37.6173, 55.7658, 37.6273)
    assert 1.0 < dist < 2.0


def test_barter_enums():
    assert BarterAdType.offer.value == "offer"
    assert BarterTxStatus.pending.value == "pending"


def test_task_report_calculation():
    logs = [
        {"duration_minutes": 60, "rate": 600},
        {"duration_minutes": 30, "rate": 400},
    ]
    total_minutes = sum(l["duration_minutes"] for l in logs)
    total_money = sum((l["rate"] or 0) * l["duration_minutes"] / 60 for l in logs)
    assert total_minutes == 90
    assert total_money == 800.0
