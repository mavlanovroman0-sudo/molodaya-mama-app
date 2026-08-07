"""BLE «Красная кнопка» webhook / Red button BLE integration."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import BleDevice, User
from app.services.auth import get_current_user

router = APIRouter(prefix="/ble", tags=["ble"])


class BlePressEvent(BaseModel):
    device_mac: str
    action: str = "quiet_hour"  # тихий час / silent mode


class BleRegisterRequest(BaseModel):
    device_mac: str


@router.post("/register")
async def register_ble(
    body: BleRegisterRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Привязка BLE-брелока к аккаунту."""
    result = await db.execute(select(BleDevice).where(BleDevice.device_mac == body.device_mac))
    existing = result.scalar_one_or_none()
    if existing:
        existing.user_id = user.id
        existing.last_seen_at = datetime.now(timezone.utc)
    else:
        db.add(BleDevice(user_id=user.id, device_mac=body.device_mac))
    await db.flush()
    return {"status": "registered", "device_mac": body.device_mac}


@router.post("/event")
async def ble_event(
    body: BlePressEvent,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Событие от брелока (имитация).
    Только владелец зарегистрированного устройства.
    """
    result = await db.execute(select(BleDevice).where(BleDevice.device_mac == body.device_mac))
    device = result.scalar_one_or_none()
    if not device:
        return {"success": False, "error": "device_not_registered"}
    if device.user_id != user.id:
        raise HTTPException(status_code=403, detail="Device belongs to another user")

    device.last_seen_at = datetime.now(timezone.utc)
    await db.flush()

    return {
        "success": True,
        "action": body.action,
        "effects": [
            "notifications_silenced",
            "white_noise_started",
            "partner_notified_optional",
        ],
        "message": "Режим «Тихий час» активирован",
    }
