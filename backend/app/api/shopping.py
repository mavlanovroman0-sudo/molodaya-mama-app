"""Списки покупок / Shopping lists API."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import User
from app.models_features import ShoppingItem, ShoppingList
from app.services.auth import get_current_user

router = APIRouter(prefix="/shopping", tags=["shopping"])


class ListCreate(BaseModel):
    name: str = "Список покупок"


class ListUpdate(BaseModel):
    name: str


class ItemCreate(BaseModel):
    list_id: UUID
    name: str
    quantity: float | None = 1
    unit: str | None = None


class ItemUpdate(BaseModel):
    name: str | None = None
    quantity: float | None = None
    unit: str | None = None
    is_bought: bool | None = None


@router.get("/lists")
async def get_lists(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ShoppingList).where(ShoppingList.user_id == user.id).options(selectinload(ShoppingList.items))
    )
    lists = result.scalars().all()
    return [
        {
            "id": str(l.id),
            "name": l.name,
            "items_count": len(l.items),
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in lists
    ]


@router.post("/lists", status_code=201)
async def create_list(body: ListCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    lst = ShoppingList(user_id=user.id, name=body.name)
    db.add(lst)
    await db.flush()
    return {"id": str(lst.id), "name": lst.name}


@router.put("/lists/{list_id}")
async def update_list(
    list_id: UUID, body: ListUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    lst = await _get_list(db, user, list_id)
    lst.name = body.name
    await db.flush()
    return {"id": str(lst.id), "name": lst.name}


@router.delete("/lists/{list_id}", status_code=204)
async def delete_list(list_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    lst = await _get_list(db, user, list_id)
    await db.delete(lst)


@router.get("/items/{list_id}")
async def get_items(list_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _get_list(db, user, list_id)
    result = await db.execute(select(ShoppingItem).where(ShoppingItem.list_id == list_id))
    items = result.scalars().all()
    return [_item_dict(i) for i in items]


@router.post("/items", status_code=201)
async def create_item(body: ItemCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _get_list(db, user, body.list_id)
    item = ShoppingItem(list_id=body.list_id, name=body.name, quantity=body.quantity, unit=body.unit)
    db.add(item)
    await db.flush()
    return _item_dict(item)


@router.put("/items/{item_id}")
async def update_item(
    item_id: UUID, body: ItemUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    item = await _get_item(db, user, item_id)
    if body.name is not None:
        item.name = body.name
    if body.quantity is not None:
        item.quantity = body.quantity
    if body.unit is not None:
        item.unit = body.unit
    if body.is_bought is not None:
        item.is_bought = body.is_bought
    await db.flush()
    return _item_dict(item)


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = await _get_item(db, user, item_id)
    await db.delete(item)


async def _get_list(db: AsyncSession, user: User, list_id: UUID) -> ShoppingList:
    result = await db.execute(
        select(ShoppingList).where(ShoppingList.id == list_id, ShoppingList.user_id == user.id)
    )
    lst = result.scalar_one_or_none()
    if not lst:
        raise HTTPException(404, "List not found")
    return lst


async def _get_item(db: AsyncSession, user: User, item_id: UUID) -> ShoppingItem:
    result = await db.execute(
        select(ShoppingItem)
        .join(ShoppingList)
        .where(ShoppingItem.id == item_id, ShoppingList.user_id == user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Item not found")
    return item


def _item_dict(i: ShoppingItem) -> dict:
    return {
        "id": str(i.id),
        "list_id": str(i.list_id),
        "name": i.name,
        "quantity": i.quantity,
        "unit": i.unit,
        "is_bought": i.is_bought,
    }
