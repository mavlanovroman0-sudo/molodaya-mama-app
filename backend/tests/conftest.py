"""Общие фикстуры pytest / Shared pytest fixtures."""

import os

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import engine

# В тестах подписка включена — регистрация автоматически даёт trial
os.environ.setdefault("SUBSCRIPTION_ENFORCE", "true")


@pytest.fixture(scope="session")
async def client():
    """HTTP-клиент для интеграционных тестов (session loop — без конфликта asyncpg)."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await engine.dispose()
