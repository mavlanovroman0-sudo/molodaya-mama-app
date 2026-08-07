"""Health check endpoints."""

from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine

router = APIRouter(tags=["health"])


@router.get("/health/ready")
async def health_ready():
    """Проверка готовности: подключение к PostgreSQL."""
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}
