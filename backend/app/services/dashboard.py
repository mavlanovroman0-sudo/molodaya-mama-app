"""Конфигурация ролевых дашбордов / Role dashboard features."""

from app.models import UserRole
from app.schemas import DashboardFeature, DashboardResponse


HOUSEWIFE_FEATURES: list[DashboardFeature] = [
    DashboardFeature(id="price_scout", title_key="features.price_scout", icon="search", route="/housewife/price-scout"),
    DashboardFeature(id="invisible_salary", title_key="features.invisible_salary", icon="wallet", route="/housewife/invisible-salary"),
    DashboardFeature(id="subscription_hunter", title_key="features.subscription_hunter", icon="credit-card", route="/housewife/subscriptions"),
    DashboardFeature(id="ship_in_bottle", title_key="features.ship_in_bottle", icon="mic", route="/housewife/voice-simple"),
    DashboardFeature(id="taste_world", title_key="features.taste_world", icon="camera", route="/housewife/ingredient-translator"),
    DashboardFeature(id="anti_burnout", title_key="features.anti_burnout", icon="heart", route="/housewife/anti-burnout"),
    DashboardFeature(id="duty_exchange", title_key="features.duty_exchange", icon="map", route="/housewife/barter"),
    DashboardFeature(id="red_button", title_key="features.red_button", icon="bluetooth", route="/housewife/red-button"),
    DashboardFeature(id="delivery", title_key="features.delivery", icon="truck", route="/shared/delivery"),
    DashboardFeature(id="smart_home", title_key="features.smart_home", icon="home", route="/shared/smart-home"),
    DashboardFeature(id="vehicle", title_key="features.vehicle", icon="car", route="/shared/vehicle"),
]

YOUNG_MOM_FEATURES: list[DashboardFeature] = [
    DashboardFeature(id="silence_mode", title_key="features.silence_mode", icon="moon", route="/mom/silence"),
    DashboardFeature(id="feeding_tracker", title_key="features.feeding_tracker", icon="baby", route="/mom/feeding"),
    DashboardFeature(id="urgent_sleep", title_key="features.urgent_sleep", icon="alarm", route="/mom/urgent-sleep"),
    DashboardFeature(id="milk_calculator", title_key="features.milk_calculator", icon="calculator", route="/mom/milk"),
    DashboardFeature(id="sleep_consultant", title_key="features.sleep_consultant", icon="video", route="/mom/consultant"),
    DashboardFeature(id="voice_diary", title_key="features.voice_diary", icon="book", route="/mom/voice-diary"),
    DashboardFeature(id="nanny_search", title_key="features.nanny_search", icon="users", route="/mom/nanny"),
    DashboardFeature(id="age_checklist", title_key="features.age_checklist", icon="list", route="/mom/checklist"),
    DashboardFeature(id="partner_challenge", title_key="features.partner_challenge", icon="trophy", route="/mom/partner"),
    DashboardFeature(id="doctor_visits", title_key="features.doctor_visits", icon="calendar", route="/mom/doctor"),
    DashboardFeature(id="emotional_compass", title_key="features.emotional_compass", icon="compass", route="/mom/emotional"),
    DashboardFeature(id="kids_exchange", title_key="features.kids_exchange", icon="refresh", route="/mom/kids-exchange"),
    DashboardFeature(id="one_hand_ui", title_key="features.one_hand_ui", icon="hand", route="/mom/one-hand"),
    DashboardFeature(id="nursery_climate", title_key="features.nursery_climate", icon="thermometer", route="/mom/nursery"),
    DashboardFeature(id="mom_comic", title_key="features.mom_comic", icon="smile", route="/mom/comic"),
    DashboardFeature(id="delivery", title_key="features.delivery", icon="truck", route="/shared/delivery"),
    DashboardFeature(id="smart_home", title_key="features.smart_home", icon="home", route="/shared/smart-home"),
]


def get_dashboard(role: UserRole, token_balance: int, district: str | None) -> DashboardResponse:
    features = HOUSEWIFE_FEATURES if role == UserRole.housewife else YOUNG_MOM_FEATURES
    return DashboardResponse(
        role=role,
        features=features,
        token_balance=token_balance,
        shared_data={"district": district, "delivery_enabled": True},
    )
