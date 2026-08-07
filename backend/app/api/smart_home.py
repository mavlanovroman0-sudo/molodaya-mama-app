"""Локальный умный дом / Local smart home API (без облака)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.models_features import DeviceScenario, HomeDevice
from app.services.auth import get_current_user

router = APIRouter(tags=["local-smart-home"])


class DeviceCreate(BaseModel):
    name: str
    device_type: str = "light"
    is_on: bool = False
    value: float | None = None


class DeviceUpdate(BaseModel):
    name: str | None = None
    is_on: bool | None = None
    value: float | None = None


class ScenarioCreate(BaseModel):
    name: str
    actions: list[dict] = []


@router.get("/devices")
async def list_devices(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HomeDevice).where(HomeDevice.user_id == user.id))
    return [_dev_dict(d) for d in result.scalars().all()]


@router.post("/devices", status_code=201)
async def create_device(body: DeviceCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    dev = HomeDevice(user_id=user.id, **body.model_dump())
    db.add(dev)
    await db.flush()
    return _dev_dict(dev)


@router.put("/devices/{device_id}")
async def update_device(
    device_id: UUID, body: DeviceUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    dev = await _get_device(db, user, device_id)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(dev, k, v)
    await db.flush()
    return _dev_dict(dev)


@router.delete("/devices/{device_id}", status_code=204)
async def delete_device(device_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    dev = await _get_device(db, user, device_id)
    await db.delete(dev)


@router.get("/scenarios")
async def list_scenarios(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeviceScenario).where(DeviceScenario.user_id == user.id))
    return [_sc_dict(s) for s in result.scalars().all()]


@router.post("/scenarios", status_code=201)
async def create_scenario(
    body: ScenarioCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    sc = DeviceScenario(user_id=user.id, name=body.name, actions=body.actions)
    db.add(sc)
    await db.flush()
    return _sc_dict(sc)


@router.post("/scenarios/{scenario_id}/run")
async def run_scenario(
    scenario_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DeviceScenario).where(DeviceScenario.id == scenario_id, DeviceScenario.user_id == user.id)
    )
    sc = result.scalar_one_or_none()
    if not sc:
        raise HTTPException(404, "Scenario not found")
    applied = []
    for action in sc.actions or []:
        dev_id = action.get("device_id")
        cmd = action.get("action", "toggle")
        if not dev_id:
            continue
        dev_result = await db.execute(
            select(HomeDevice).where(HomeDevice.id == UUID(dev_id), HomeDevice.user_id == user.id)
        )
        dev = dev_result.scalar_one_or_none()
        if not dev:
            continue
        if cmd == "on":
            dev.is_on = True
        elif cmd == "off":
            dev.is_on = False
        elif cmd == "set_value" and "value" in action:
            dev.value = action["value"]
        applied.append({"device_id": dev_id, "action": cmd})
    await db.flush()
    return {"scenario": sc.name, "applied": applied}


async def _get_device(db: AsyncSession, user: User, device_id: UUID) -> HomeDevice:
    result = await db.execute(select(HomeDevice).where(HomeDevice.id == device_id, HomeDevice.user_id == user.id))
    dev = result.scalar_one_or_none()
    if not dev:
        raise HTTPException(404, "Device not found")
    return dev


def _dev_dict(d: HomeDevice) -> dict:
    return {
        "id": str(d.id),
        "name": d.name,
        "device_type": d.device_type,
        "is_on": d.is_on,
        "value": d.value,
    }


def _sc_dict(s: DeviceScenario) -> dict:
    return {"id": str(s.id), "name": s.name, "actions": s.actions or []}
