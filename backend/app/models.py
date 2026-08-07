"""SQLAlchemy модели / ORM models."""

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AppLanguage(str, enum.Enum):
    ru = "ru"
    kk = "kk"
    uz = "uz"
    tg = "tg"
    ka = "ka"
    ky = "ky"


class UserRole(str, enum.Enum):
    housewife = "housewife"
    young_mom = "young_mom"


class StoreType(str, enum.Enum):
    grocery = "grocery"
    household = "household"
    pharmacy = "pharmacy"
    baby = "baby"
    restaurant = "restaurant"
    cafe = "cafe"


class DeviceProtocol(str, enum.Enum):
    matter = "matter"
    zigbee = "zigbee"
    home_assistant = "home_assistant"
    yandex = "yandex"
    google = "google"
    homekit = "homekit"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    active_role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.housewife)
    language: Mapped[AppLanguage] = mapped_column(Enum(AppLanguage), default=AppLanguage.ru)
    auto_detect_language: Mapped[bool] = mapped_column(Boolean, default=True)
    latitude: Mapped[float | None] = mapped_column()
    longitude: Mapped[float | None] = mapped_column()
    district: Mapped[str | None] = mapped_column(String(200))
    microdistrict: Mapped[str | None] = mapped_column(String(200))
    city: Mapped[str | None] = mapped_column(String(100))
    country_code: Mapped[str] = mapped_column(String(2), default="RU")
    address_manual: Mapped[str | None] = mapped_column(Text)
    token_balance: Mapped[int] = mapped_column(Integer, default=0)
    referral_code: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    fcm_token: Mapped[str | None] = mapped_column(Text)
    expo_push_token: Mapped[str | None] = mapped_column(Text)
    is_nanny: Mapped[bool] = mapped_column(Boolean, default=False)
    trial_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    role_profiles: Mapped[list["RoleProfile"]] = relationship(back_populates="user")
    favorite_stores: Mapped[list["FavoriteStore"]] = relationship(back_populates="user")
    smart_devices: Mapped[list["SmartDevice"]] = relationship(back_populates="user")
    babies: Mapped[list["Baby"]] = relationship(back_populates="user")
    referrals_sent: Mapped[list["Referral"]] = relationship(
        back_populates="referrer", foreign_keys="Referral.referrer_id"
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")

    def add_jetons(self, amount: int) -> None:
        """Начисление жетонов / Add tokens to balance."""
        self.token_balance = (self.token_balance or 0) + amount


class Referral(Base):
    """Реферальная связь / Referral link between users."""

    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    referrer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    referee_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    referral_code: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    bonus_given: Mapped[bool] = mapped_column(Boolean, default=False)

    referrer: Mapped["User"] = relationship(back_populates="referrals_sent", foreign_keys=[referrer_id])


class TokenTransaction(Base):
    """История начисления жетонов / Token (jeton) ledger."""

    __tablename__ = "token_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    amount: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RoleProfile(Base):
    __tablename__ = "role_profiles"
    __table_args__ = (UniqueConstraint("user_id", "role"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    settings: Mapped[dict] = mapped_column(JSONB, insert_default=dict)
    dashboard_layout: Mapped[list] = mapped_column(JSONB, insert_default=list)

    user: Mapped["User"] = relationship(back_populates="role_profiles")


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    store_type: Mapped[StoreType] = mapped_column(Enum(StoreType))
    address: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column()
    longitude: Mapped[float | None] = mapped_column()
    district: Mapped[str | None] = mapped_column(String(200))
    country_code: Mapped[str] = mapped_column(String(2), default="RU")
    delivery_available: Mapped[bool] = mapped_column(Boolean, default=False)
    delivery_radius_km: Mapped[int | None] = mapped_column(Integer, default=5)
    delivery_api_url: Mapped[str | None] = mapped_column(Text)
    website_url: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, insert_default=dict)


class FavoriteStore(Base):
    __tablename__ = "favorite_stores"
    __table_args__ = (UniqueConstraint("user_id", "store_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    store_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stores.id", ondelete="CASCADE"))
    notes: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="favorite_stores")
    store: Mapped["Store"] = relationship()


class SmartDevice(Base):
    __tablename__ = "smart_devices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    room: Mapped[str | None] = mapped_column(String(50))
    device_type: Mapped[str | None] = mapped_column(String(50))
    protocol: Mapped[DeviceProtocol] = mapped_column(Enum(DeviceProtocol))
    external_id: Mapped[str | None] = mapped_column(String(255))
    provider_config: Mapped[dict] = mapped_column(JSONB, insert_default=dict)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    last_state: Mapped[dict] = mapped_column(JSONB, insert_default=dict)

    user: Mapped["User"] = relationship(back_populates="smart_devices")


class Baby(Base):
    __tablename__ = "babies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    birth_date: Mapped[date] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(10))

    user: Mapped["User"] = relationship(back_populates="babies")
    feeding_logs: Mapped[list["FeedingLog"]] = relationship(back_populates="baby")
    sleep_logs: Mapped[list["SleepLog"]] = relationship(back_populates="baby")
    diaper_logs: Mapped[list["DiaperLog"]] = relationship(back_populates="baby")


class FeedingLog(Base):
    __tablename__ = "feeding_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    baby_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("babies.id", ondelete="CASCADE"))
    feeding_type: Mapped[str | None] = mapped_column(String(20))
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    amount_ml: Mapped[int | None] = mapped_column(Integer)
    side: Mapped[str | None] = mapped_column(String(10))
    notes: Mapped[str | None] = mapped_column(Text)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    baby: Mapped["Baby"] = relationship(back_populates="feeding_logs")


class SleepLog(Base):
    __tablename__ = "sleep_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    baby_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("babies.id", ondelete="CASCADE"))
    sleep_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sleep_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    quality: Mapped[str | None] = mapped_column(String(20))
    phase_prediction: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)

    baby: Mapped["Baby"] = relationship(back_populates="sleep_logs")


class DiaperLog(Base):
    __tablename__ = "diaper_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    baby_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("babies.id", ondelete="CASCADE"))
    diaper_type: Mapped[str | None] = mapped_column(String(20))
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    baby: Mapped["Baby"] = relationship(back_populates="diaper_logs")


class Barter(Base):
    __tablename__ = "barters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    district: Mapped[str | None] = mapped_column(String(200))
    tokens_offered: Mapped[int] = mapped_column(Integer, default=0)


class StressScore(Base):
    __tablename__ = "stress_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    score: Mapped[int] = mapped_column(Integer)
    source: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BleDevice(Base):
    __tablename__ = "ble_devices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    device_mac: Mapped[str | None] = mapped_column(String(17), unique=True)
    nickname: Mapped[str] = mapped_column(String(50), default="Красная кнопка")
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class VehicleSettings(Base):
    __tablename__ = "vehicle_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    make: Mapped[str | None] = mapped_column(String(50))
    model: Mapped[str | None] = mapped_column(String(50))
    integration_type: Mapped[str | None] = mapped_column(String(50))
    api_config: Mapped[dict] = mapped_column(JSONB, insert_default=dict)
    child_mode_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    fuel_reminder_km: Mapped[int | None] = mapped_column(Integer)


# Модели функций профилей / Profile feature models
from app.models_features import (  # noqa: E402, F401
    BabyChecklist,
    BabyDiaper,
    BabyFeed,
    BabySleep,
    BarterAd,
    BarterTransaction,
    DeviceScenario,
    HomeDevice,
    NannyRequest,
    ShoppingItem,
    ShoppingList,
    TaskLog,
    UserTask,
)
from app.models_subscription import Subscription, SubscriptionPlan, SubscriptionStatus  # noqa: E402, F401
