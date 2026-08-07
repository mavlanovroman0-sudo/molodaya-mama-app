"""Умный дом / Smart home devices."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import SmartDevice, User
from app.schemas import DeviceCommandRequest, SmartDeviceCreate, SmartDeviceResponse
from app.services.auth import get_current_user
from app.services.smart_home.service import execute_device_command, list_user_devices

router = APIRouter(prefix="/smart-home", tags=["smart-home"])


@router.get("/devices", response_model=list[SmartDeviceResponse])
async def devices(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await list_user_devices(db, user)


@router.post("/devices", response_model=SmartDeviceResponse, status_code=201)
async def add_device(
    body: SmartDeviceCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    device = SmartDevice(user_id=user.id, **body.model_dump())
    db.add(device)
    await db.flush()
    return device


@router.post("/devices/{device_id}/command")
async def send_command(
    device_id: UUID,
    body: DeviceCommandRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Команда устройству: on, off, set_temperature, start_scenario и т.д."""
    result = await execute_device_command(db, user, device_id, body.command, body.params)
    if not result.get("success", True) and result.get("error"):
        raise HTTPException(status_code=404, detail=result["error"])
    return result
