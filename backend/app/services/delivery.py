"""Доставка: избранные магазины + слоты / Delivery hub service."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import FavoriteStore, Store, User
from app.schemas import DeliveryHubResponse, DeliverySlotResponse, StoreResponse


async def get_delivery_hub(db: AsyncSession, user: User) -> DeliveryHubResponse:
    """Единый экран доставки: избранные магазины с доступными слотами в районе."""
    result = await db.execute(
        select(FavoriteStore)
        .where(FavoriteStore.user_id == user.id)
        .options(selectinload(FavoriteStore.store))
    )
    favorites = result.scalars().all()
    stores = [f.store for f in favorites if f.store]

    # Фильтр по району пользователя
    if user.district:
        stores = [s for s in stores if not s.district or s.district == user.district]

    slots: list[DeliverySlotResponse] = []
    now = datetime.now(timezone.utc)
    for store in stores:
        if store.delivery_available:
            # MVP: симуляция слотов (в проде — парсинг/API агрегаторов)
            for i in range(3):
                start = now + timedelta(hours=2 + i * 2)
                slots.append(
                    DeliverySlotResponse(
                        store_id=store.id,
                        store_name=store.name,
                        slot_start=start,
                        slot_end=start + timedelta(hours=2),
                        is_available=True,
                        price_estimate=199.0 + i * 50,
                    )
                )

    return DeliveryHubResponse(
        district=user.district,
        favorite_stores=[StoreResponse.model_validate(s) for s in stores],
        available_slots=slots,
    )


async def add_favorite_store(db: AsyncSession, user: User, store_id: UUID, notes: str | None) -> FavoriteStore:
    fav = FavoriteStore(user_id=user.id, store_id=store_id, notes=notes)
    db.add(fav)
    await db.flush()
    return fav
