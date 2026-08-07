"""Auth & registration with auto-localization."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import RoleProfile, User, UserRole
from app.schemas import (
    GeoDetectResponse,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth import create_access_token, get_current_user, hash_password, verify_password
from app.services.geo import detect_location
from app.services.subscription import start_trial, user_has_access

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.post("/register", response_model=TokenResponse)
async def register(
    body: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Регистрация + автоопределение языка и района."""
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    geo: GeoDetectResponse = await detect_location(
        ip=_client_ip(request),
        accept_language=request.headers.get("accept-language"),
    )

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        display_name=body.display_name,
        language=geo.language,
        country_code=geo.country_code,
        city=geo.city,
        district=geo.district,
        microdistrict=geo.microdistrict,
        latitude=geo.latitude,
        longitude=geo.longitude,
    )
    db.add(user)
    await db.flush()

    for role in UserRole:
        db.add(RoleProfile(user_id=user.id, role=role))

    if not user.trial_used:
        await start_trial(db, user)

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Повторный trial запрещён: только при первой регистрации (trial_used=False)
    if not await user_has_access(db, user.id) and not user.trial_used:
        await start_trial(db, user)

    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return user
