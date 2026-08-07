"""Seed-скрипт: тестовые магазины для 6 стран / Test stores for delivery."""

import asyncio
import os
import uuid

import asyncpg

# Данные: минимум 2 магазина на страну (один с доставкой, один без)
STORES = [
    # Россия
    {"name": "Пятёрочка", "country_code": "RU", "lat": 55.7558, "lon": 37.6173, "delivery": True, "radius": 8},
    {"name": "Магнит", "country_code": "RU", "lat": 55.76, "lon": 37.62, "delivery": False, "radius": 0},
    # Казахстан
    {"name": "Magnum", "country_code": "KZ", "lat": 43.238, "lon": 76.945, "delivery": True, "radius": 10},
    {"name": "Арзан", "country_code": "KZ", "lat": 43.24, "lon": 76.95, "delivery": False, "radius": 0},
    # Узбекистан
    {"name": "Korzinka", "country_code": "UZ", "lat": 41.311, "lon": 69.279, "delivery": True, "radius": 7},
    {"name": "Havas", "country_code": "UZ", "lat": 41.315, "lon": 69.28, "delivery": False, "radius": 0},
    # Таджикистан
    {"name": "Сафед", "country_code": "TJ", "lat": 38.559, "lon": 68.787, "delivery": True, "radius": 6},
    {"name": "Ориён", "country_code": "TJ", "lat": 38.56, "lon": 68.79, "delivery": False, "radius": 0},
    # Грузия
    {"name": "Carrefour", "country_code": "GE", "lat": 41.715, "lon": 44.827, "delivery": True, "radius": 9},
    {"name": "Nikora", "country_code": "GE", "lat": 41.72, "lon": 44.83, "delivery": False, "radius": 0},
    # Киргизия
    {"name": "Globus", "country_code": "KG", "lat": 42.874, "lon": 74.612, "delivery": True, "radius": 8},
    {"name": "Frunze", "country_code": "KG", "lat": 42.88, "lon": 74.61, "delivery": False, "radius": 0},
]


def _database_url() -> str:
    url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://homeease:homeease_dev@localhost:5432/homeease",
    )
    return url.replace("postgresql+asyncpg://", "postgresql://")


async def seed() -> None:
    conn = await asyncpg.connect(_database_url())
    try:
        await conn.execute(
            "ALTER TABLE stores ADD COLUMN IF NOT EXISTS country_code CHAR(2) DEFAULT 'RU'"
        )
        await conn.execute(
            "ALTER TABLE stores ADD COLUMN IF NOT EXISTS delivery_radius_km INTEGER DEFAULT 5"
        )
        has_slots = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'delivery_slots')"
        )
        await conn.execute("DELETE FROM favorite_stores")
        if has_slots:
            await conn.execute("DELETE FROM delivery_slots")
        await conn.execute("DELETE FROM stores")

        for s in STORES:
            await conn.execute(
                """
                INSERT INTO stores (
                    id, name, store_type, latitude, longitude,
                    country_code, delivery_available, delivery_radius_km, district, metadata
                ) VALUES ($1, $2, 'grocery', $3, $4, $5, $6, $7, $8, '{}'::jsonb)
                """,
                uuid.uuid4(),
                s["name"],
                s["lat"],
                s["lon"],
                s["country_code"],
                s["delivery"],
                s["radius"] if s["delivery"] else None,
                s["country_code"],
            )
        count = await conn.fetchval("SELECT COUNT(*) FROM stores")
        print(f"✓ Seeded {count} stores")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed())
