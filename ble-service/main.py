"""BLE mock service — имитация брелока «Красная кнопка»."""

import os

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="HomeEase BLE Mock", version="1.0.0")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class SimulatedPress(BaseModel):
    device_mac: str = "AA:BB:CC:DD:EE:FF"
    action: str = "quiet_hour"


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ble-mock"}


@app.post("/simulate-press")
async def simulate_press(body: SimulatedPress):
    """
    Имитация нажатия физического BLE-брелока.
    В мобильном приложении: react-native-ble-manager слушает характеристику.
    В браузере: Web Bluetooth API (если поддерживается).
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BACKEND_URL}/api/v1/ble/event",
            json=body.model_dump(),
            timeout=10.0,
        )
        return resp.json()


@app.get("/scan")
async def scan_devices():
    """Имитация сканирования BLE устройств."""
    return {
        "devices": [
            {"mac": "AA:BB:CC:DD:EE:FF", "name": "HomeEase Red Button", "rssi": -45},
            {"mac": "11:22:33:44:55:66", "name": "HomeEase Red Button 2", "rssi": -62},
        ]
    }
