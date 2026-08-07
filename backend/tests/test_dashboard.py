"""Тесты дашборда / Dashboard tests."""

from app.models import UserRole
from app.services.dashboard import get_dashboard, HOUSEWIFE_FEATURES, YOUNG_MOM_FEATURES


def test_housewife_dashboard_has_8_plus_features():
    dash = get_dashboard(UserRole.housewife, 100, "Центральный")
    assert dash.role == UserRole.housewife
    assert len(dash.features) >= 8
    assert any(f.id == "price_scout" for f in dash.features)


def test_young_mom_dashboard_has_15_features():
    dash = get_dashboard(UserRole.young_mom, 50, "Алматы-1")
    assert len([f for f in dash.features if f.id not in ("delivery", "smart_home")]) >= 15


def test_shared_delivery_in_both_roles():
    hw = get_dashboard(UserRole.housewife, 0, None)
    mom = get_dashboard(UserRole.young_mom, 0, None)
    assert any(f.id == "delivery" for f in hw.features)
    assert any(f.id == "delivery" for f in mom.features)
