"""Интеграционные тесты новых эндпоинтов / Feature API tests."""

import uuid

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def _register(client: AsyncClient, email: str | None = None) -> str:
    email = email or f"test_{uuid.uuid4().hex[:8]}@example.com"
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "display_name": "Tester"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.mark.asyncio(loop_scope="session")
async def test_subscription_trial_grants_api_access(client, monkeypatch):
    """Регистрация даёт trial — middleware пропускает защищённые эндпоинты."""
    from app.config import settings

    monkeypatch.setattr(settings, "subscription_enforce", True)
    token = await _register(client)
    headers = {"Authorization": f"Bearer {token}"}

    status = await client.get("/api/v1/user/subscription-status", headers=headers)
    assert status.status_code == 200
    assert status.json()["has_access"] is True

    status = await client.get("/api/v1/user/subscription-status", headers=headers)
    assert status.status_code == 200
    data = status.json()
    assert data["status"] == "trialing"
    assert data["has_access"] is True
    assert data["days_remaining"] >= 13
    assert "pricing" in data

    lists = await client.get("/api/v1/shopping/lists", headers=headers)
    assert lists.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_shopping_list_crud(client):
    token = await _register(client)
    headers = {"Authorization": f"Bearer {token}"}

    create = await client.post("/api/v1/shopping/lists", json={"name": "Продукты"}, headers=headers)
    assert create.status_code == 201
    list_id = create.json()["id"]

    lists = await client.get("/api/v1/shopping/lists", headers=headers)
    assert lists.status_code == 200
    assert any(l["id"] == list_id for l in lists.json())

    item = await client.post(
        "/api/v1/shopping/items",
        json={"list_id": list_id, "name": "Молоко", "quantity": 2, "unit": "л"},
        headers=headers,
    )
    assert item.status_code == 201

    items = await client.get(f"/api/v1/shopping/items/{list_id}", headers=headers)
    assert items.status_code == 200
    assert len(items.json()) == 1


@pytest.mark.asyncio(loop_scope="session")
async def test_task_and_report(client):
    token = await _register(client)
    headers = {"Authorization": f"Bearer {token}"}

    task = await client.post(
        "/api/v1/tasks",
        json={"name": "Уборка", "default_duration_minutes": 60, "default_rate": 500},
        headers=headers,
    )
    assert task.status_code == 201
    task_id = task.json()["id"]

    log = await client.post(
        "/api/v1/task_logs",
        json={"task_id": task_id, "duration_minutes": 45, "rate": 500},
        headers=headers,
    )
    assert log.status_code == 201

    report = await client.get("/api/v1/task_logs/report", headers=headers)
    assert report.status_code == 200
    assert report.json()["total_minutes"] == 45


@pytest.mark.asyncio(loop_scope="session")
async def test_baby_feed_create(client):
    token = await _register(client)
    headers = {"Authorization": f"Bearer {token}"}

    feed = await client.post(
        "/api/v1/baby/feeds",
        json={"baby_name": "Алиса", "feed_type": "breast", "duration_minutes": 15},
        headers=headers,
    )
    assert feed.status_code == 201

    feeds = await client.get("/api/v1/baby/feeds", headers=headers)
    assert feeds.status_code == 200
    assert len(feeds.json()) >= 1


@pytest.mark.asyncio(loop_scope="session")
async def test_local_smart_home_device(client):
    token = await _register(client)
    headers = {"Authorization": f"Bearer {token}"}

    dev = await client.post(
        "/api/v1/devices",
        json={"name": "Свет в кухне", "device_type": "light", "is_on": True},
        headers=headers,
    )
    assert dev.status_code == 201

    devices = await client.get("/api/v1/devices", headers=headers)
    assert devices.status_code == 200
    assert len(devices.json()) == 1
