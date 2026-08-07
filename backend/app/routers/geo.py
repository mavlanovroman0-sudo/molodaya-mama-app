"""Геолокация и локализация / Geo & i18n endpoints."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import GeoDetectRequest, GeoDetectResponse, LanguageUpdate, ManualAddressUpdate, UserResponse
from app.services.auth import get_current_user
from app.services.geo import detect_location

router = APIRouter(prefix="/geo", tags=["geo", "localization"])


def _resolve_ip(body: GeoDetectRequest, request: Request) -> str | None:
    ip = body.ip
    if not ip and request.client:
        forwarded = request.headers.get("x-forwarded-for")
        ip = forwarded.split(",")[0].strip() if forwarded else request.client.host
    return ip


@router.post("/detect", response_model=GeoDetectResponse)
async def detect_geo(body: GeoDetectRequest, request: Request):
    """
    Автоопределение языка и района.
    Принимает IP (авто из заголовков), координаты GPS или Accept-Language.
    """
    return await detect_location(
        ip=_resolve_ip(body, request),
        latitude=body.latitude,
        longitude=body.longitude,
        accept_language=body.accept_language or request.headers.get("accept-language"),
    )


@router.post("/apply", response_model=UserResponse)
async def apply_geo_to_user(
    body: GeoDetectRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Применить автоопределение к текущему пользователю (при каждом входе если включено)."""
    if not user.auto_detect_language:
        return user

    geo = await detect_location(
        ip=_resolve_ip(body, request),
        latitude=body.latitude,
        longitude=body.longitude,
        accept_language=body.accept_language or request.headers.get("accept-language"),
    )
    user.language = geo.language
    user.country_code = geo.country_code
    user.city = geo.city
    user.district = geo.district
    user.microdistrict = geo.microdistrict
    if geo.latitude:
        user.latitude = geo.latitude
    if geo.longitude:
        user.longitude = geo.longitude
    await db.flush()
    return user


@router.patch("/language", response_model=UserResponse)
async def update_language(
    body: LanguageUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Ручная смена языка."""
    user.language = body.language
    if body.auto_detect_language is not None:
        user.auto_detect_language = body.auto_detect_language
    await db.flush()
    return user


@router.patch("/address", response_model=UserResponse)
async def set_manual_address(
    body: ManualAddressUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Ручной адрес если геолокация отключена."""
    user.address_manual = body.address_manual
    if body.city:
        user.city = body.city
    if body.district:
        user.district = body.district
    await db.flush()
    return user
