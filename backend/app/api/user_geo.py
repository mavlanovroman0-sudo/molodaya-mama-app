"""Геолокация пользователя и поиск нянь / User location & nanny search."""

import math
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.models_features import NannyRequest
from app.services.auth import get_current_user
from app.services.expo_push import send_expo_push

router = APIRouter(tags=["user-geo"])


class LocationUpdate(BaseModel):
    latitude: float
    longitude: float


class NannyRequestBody(BaseModel):
    to_user_id: UUID
    message: str | None = None


class NannyProfileUpdate(BaseModel):
    is_nanny: bool


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371
    p = math.pi / 180
    a = 0.5 - math.cos((lat2 - lat1) * p) / 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * (1 - math.cos((lon2 - lon1) * p)) / 2
    return 2 * r * math.asin(math.sqrt(a))


@router.put("/user/nanny")
async def update_nanny_profile(
    body: NannyProfileUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    user.is_nanny = body.is_nanny
    await db.flush()
    return {"is_nanny": user.is_nanny}


@router.put("/user/location")
async def update_location(
    body: LocationUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    user.latitude = body.latitude
    user.longitude = body.longitude
    await db.flush()
    return {"latitude": user.latitude, "longitude": user.longitude}


@router.get("/nannies")
async def find_nannies(
    radius_km: float = Query(10, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.latitude is None or user.longitude is None:
        return {"nannies": [], "message": "location_required"}
    result = await db.execute(select(User).where(User.is_nanny.is_(True), User.id != user.id))
    nannies = []
    for n in result.scalars().all():
        if n.latitude is None or n.longitude is None:
            continue
        dist = _haversine_km(user.latitude, user.longitude, n.latitude, n.longitude)
        if dist <= radius_km:
            nannies.append({
                "id": str(n.id),
                "display_name": n.display_name or n.email,
                "distance_km": round(dist, 2),
                "latitude": n.latitude,
                "longitude": n.longitude,
            })
    nannies.sort(key=lambda x: x["distance_km"])
    return {"nannies": nannies}


@router.post("/nannies/request", status_code=201)
async def request_nanny(
    body: NannyRequestBody, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    req = NannyRequest(from_user_id=user.id, to_user_id=body.to_user_id, message=body.message)
    db.add(req)
    await db.flush()
    await send_expo_push(
        db,
        body.to_user_id,
        title="Запрос няни",
        body=body.message or "Новый запрос от мамы в «молодая мама»",
        data={"type": "nanny_request"},
    )
    return {"id": str(req.id), "status": "sent"}
