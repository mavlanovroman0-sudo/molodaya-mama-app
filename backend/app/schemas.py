"""Pydantic схемы запросов/ответов / API schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models import AppLanguage, DeviceProtocol, StoreType, UserRole


# --- Auth & User ---

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    display_name: str | None
    active_role: UserRole
    language: AppLanguage
    auto_detect_language: bool
    district: str | None
    city: str | None
    country_code: str
    token_balance: int

    model_config = {"from_attributes": True}


# --- Localization & Geo ---

class GeoDetectRequest(BaseModel):
    """IP или координаты для авто-локализации."""
    ip: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    accept_language: str | None = None


class GeoDetectResponse(BaseModel):
    language: AppLanguage
    country_code: str
    city: str | None
    district: str | None
    microdistrict: str | None
    latitude: float | None
    longitude: float | None


class LanguageUpdate(BaseModel):
    language: AppLanguage
    auto_detect_language: bool | None = None


class ManualAddressUpdate(BaseModel):
    address_manual: str
    city: str | None = None
    district: str | None = None


# --- Role switch ---

class RoleSwitchRequest(BaseModel):
    role: UserRole


class DashboardFeature(BaseModel):
    id: str
    title_key: str
    icon: str
    route: str
    enabled: bool = True


class DashboardResponse(BaseModel):
    role: UserRole
    features: list[DashboardFeature]
    token_balance: int
    shared_data: dict


# --- Stores & Delivery ---

class StoreCreate(BaseModel):
    name: str
    store_type: StoreType
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    district: str | None = None
    country_code: str = "RU"
    delivery_available: bool = False
    delivery_radius_km: int | None = None


class StoreResponse(BaseModel):
    id: UUID
    name: str
    store_type: StoreType
    address: str | None
    district: str | None
    country_code: str
    delivery_available: bool
    delivery_radius_km: int | None = None

    model_config = {"from_attributes": True}


class FavoriteStoreCreate(BaseModel):
    store_id: UUID
    notes: str | None = None


class DeliverySlotResponse(BaseModel):
    store_id: UUID
    store_name: str
    slot_start: datetime
    slot_end: datetime
    is_available: bool
    price_estimate: float | None


class DeliveryHubResponse(BaseModel):
    district: str | None
    favorite_stores: list[StoreResponse]
    available_slots: list[DeliverySlotResponse]
    multi_store_cart_supported: bool = True


# --- Smart Home ---

class SmartDeviceCreate(BaseModel):
    name: str
    room: str | None = None
    device_type: str | None = None
    protocol: DeviceProtocol
    external_id: str | None = None
    provider_config: dict = Field(default_factory=dict)


class SmartDeviceResponse(BaseModel):
    id: UUID
    name: str
    room: str | None
    device_type: str | None
    protocol: DeviceProtocol
    is_online: bool
    last_state: dict

    model_config = {"from_attributes": True}


class DeviceCommandRequest(BaseModel):
    command: str
    params: dict = Field(default_factory=dict)


# --- Baby tracker ---

class BabyCreate(BaseModel):
    name: str
    birth_date: date
    gender: str | None = None


class BabyResponse(BaseModel):
    id: UUID
    name: str
    birth_date: date
    gender: str | None

    model_config = {"from_attributes": True}


class FeedingLogCreate(BaseModel):
    feeding_type: str
    duration_minutes: int | None = None
    amount_ml: int | None = None
    side: str | None = None
    notes: str | None = None
    logged_at: datetime | None = None


class SleepLogCreate(BaseModel):
    sleep_start: datetime
    sleep_end: datetime | None = None
    quality: str | None = None
    notes: str | None = None


class DiaperLogCreate(BaseModel):
    diaper_type: str
    logged_at: datetime | None = None


class FeedingPrediction(BaseModel):
    next_peak_at: datetime | None
    evening_chaos_warning: bool
    message_key: str
    interval_hours_avg: float | None


class SleepPhasePrediction(BaseModel):
    current_phase: str
    confidence: float
    next_wake_window: datetime | None


class BabyTrackerSummary(BaseModel):
    baby: BabyResponse
    last_feeding: datetime | None
    last_sleep: datetime | None
    last_diaper: datetime | None
    feeding_prediction: FeedingPrediction
    sleep_prediction: SleepPhasePrediction | None
