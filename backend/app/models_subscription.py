"""Подписка / Subscription models."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SubscriptionStatus(str, enum.Enum):
    trialing = "trialing"
    active = "active"
    canceled = "canceled"
    past_due = "past_due"
    expired = "expired"


class SubscriptionPlan(str, enum.Enum):
    monthly = "monthly"
    yearly = "yearly"
    trial = "trial"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, native_enum=False, length=20),
        default=SubscriptionStatus.trialing,
    )
    plan: Mapped[SubscriptionPlan] = mapped_column(
        Enum(SubscriptionPlan, native_enum=False, length=20),
        default=SubscriptionPlan.trial,
    )
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    trial_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    trial_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    provider: Mapped[str] = mapped_column(String(30), default="stripe")
    provider_subscription_id: Mapped[str | None] = mapped_column(String(255), index=True)
    provider_payment_id: Mapped[str | None] = mapped_column(String(255), index=True)
    provider_customer_id: Mapped[str | None] = mapped_column(String(255))
    yookassa_payment_method_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="subscriptions")  # noqa: F821
