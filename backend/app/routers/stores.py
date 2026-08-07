"""Магазины, избранное, доставка / Stores & delivery."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Store, User
from app.schemas import DeliveryHubResponse, FavoriteStoreCreate, StoreCreate, StoreResponse
from app.services.auth import get_current_user
from app.services.cron_auth import require_cron_secret
from app.services.delivery import add_favorite_store, get_delivery_hub

router = APIRouter(prefix="/stores", tags=["stores", "delivery"])


@router.get("/delivery", response_model=DeliveryHubResponse)
async def delivery_hub(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Единый экран «Доставка» — избранные магазины + слоты в районе."""
    return await get_delivery_hub(db, user)


@router.post("/favorites", status_code=201)
async def add_favorite(
    body: FavoriteStoreCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Сохранить избранный магазин."""
    store = await db.get(Store, body.store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    fav = await add_favorite_store(db, user, body.store_id, body.notes)
    return {"id": str(fav.id), "store_id": str(body.store_id)}


@router.get("", response_model=list[StoreResponse])
async def list_stores(
    district: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Список магазинов (фильтр по району)."""
    q = select(Store)
    if district:
        q = q.where(Store.district == district)
    result = await db.execute(q.limit(50))
    return result.scalars().all()


@router.post("", response_model=StoreResponse, status_code=201, dependencies=[Depends(require_cron_secret)])
async def create_store(
    body: StoreCreate,
    db: AsyncSession = Depends(get_db),
):
    """Создать магазин (только внутренний cron / seed)."""
    store = Store(**body.model_dump())
    db.add(store)
    await db.flush()
    return store
