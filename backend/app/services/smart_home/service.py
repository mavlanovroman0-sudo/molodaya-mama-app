"""Сервис умного дома / Smart home service."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SmartDevice, User
from app.services.smart_home.providers import get_provider


async def list_user_devices(db: AsyncSession, user: User) -> list[SmartDevice]:
    result = await db.execute(select(SmartDevice).where(SmartDevice.user_id == user.id))
    return list(result.scalars().all())


async def execute_device_command(
    db: AsyncSession, user: User, device_id: UUID, command: str, params: dict
) -> dict:
    result = await db.execute(
        select(SmartDevice).where(SmartDevice.id == device_id, SmartDevice.user_id == user.id)
    )
    device = result.scalar_one_or_none()
    if not device:
        return {"success": False, "error": "device_not_found"}

    provider = get_provider(device.protocol.value, device.provider_config)
    response = await provider.send_command(device.external_id or str(device.id), command, params)
    device.last_state = {**device.last_state, **response}
    return response
