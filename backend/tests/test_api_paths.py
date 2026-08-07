"""Проверка, что все пути фронтенда зарегистрированы в FastAPI."""

import pytest
from httpx import ASGITransport, AsyncClient
FRONTEND_GET_PATHS = [
    "/api/v1/shopping/lists",
    "/api/v1/barter/ads",
    "/api/v1/tasks",
    "/api/v1/task_logs/report",
    "/api/v1/devices",
    "/api/v1/scenarios",
    "/api/v1/baby/feeds",
    "/api/v1/baby/sleep",
    "/api/v1/baby/diapers",
    "/api/v1/baby/checklist",
    "/api/v1/nannies",
    "/api/v1/referral/stats",
    "/api/v1/user/subscription-status",
    "/api/v1/subscription/prices",
    "/api/v1/config/remote",
]

FRONTEND_POST_PATHS = [
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/geo/detect",
    "/api/v1/shopping/lists",
    "/api/v1/shopping/items",
    "/api/v1/barter/ads",
    "/api/v1/tasks",
    "/api/v1/task_logs",
    "/api/v1/devices",
    "/api/v1/scenarios",
    "/api/v1/baby/feeds",
    "/api/v1/baby/sleep",
    "/api/v1/baby/diapers",
    "/api/v1/baby/checklist",
    "/api/v1/roles/switch",
    "/api/v1/ble/register",
    "/api/v1/subscription/checkout",
]


def _collect_routes(app) -> set[tuple[str, str]]:
    routes: set[tuple[str, str]] = set()
    for route in app.routes:
        methods = getattr(route, "methods", None) or set()
        path = getattr(route, "path", None)
        if path and methods:
            for method in methods:
                routes.add((method.upper(), path))
    return routes


@pytest.fixture
def app_routes():
    from app.main import app

    return _collect_routes(app)


def test_frontend_get_paths_registered(app_routes):
  missing = []
  for path in FRONTEND_GET_PATHS:
      if ("GET", path) not in app_routes:
          missing.append(path)
  assert not missing, f"GET routes missing: {missing}"


def test_frontend_post_paths_registered(app_routes):
  missing = []
  for path in FRONTEND_POST_PATHS:
      if ("POST", path) not in app_routes:
          missing.append(path)
  assert not missing, f"POST routes missing: {missing}"


@pytest.mark.asyncio(loop_scope="session")
async def test_authenticated_endpoints_return_data_not_404(client):
    """Smoke: зарегистрированный пользователь получает 200, не 404."""
    import uuid

    email = f"paths_{uuid.uuid4().hex[:8]}@demo.homeease"
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "demo1234", "role": "housewife"},
    )
    assert reg.status_code in (200, 201), reg.text

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "demo1234"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    for path in FRONTEND_GET_PATHS:
        if path.startswith("/api/v1/config"):
            continue
        resp = await client.get(path, headers=headers)
        assert resp.status_code != 404, f"{path} -> 404"
        assert resp.status_code in (200, 422), f"{path} -> {resp.status_code}: {resp.text}"
