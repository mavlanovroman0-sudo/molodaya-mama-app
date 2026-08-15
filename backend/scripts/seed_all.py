"""Полное наполнение БД демо-данными для HomeEase 2.0.

Запуск:
  docker compose -p homeease exec backend python -m scripts.seed_all
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import delete, select

from app.database import Base, async_session, engine
from app.models import RoleProfile, Store, StoreType, User, UserRole
from app.models_features import (
    BabyChecklist,
    BabyDiaper,
    BabyFeed,
    BabySleep,
    BarterAd,
    BarterAdType,
    DeviceScenario,
    HomeDevice,
    ShoppingItem,
    ShoppingList,
    TaskLog,
    UserTask,
)
from app.models_subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from app.services.auth import hash_password
from app.services.subscription import start_trial

import app.models  # noqa: F401
import app.models_features  # noqa: F401
import app.models_subscription  # noqa: F401

DEMO_PASSWORD = "demo1234"

USERS = [
    {
        "email": "housewife@demo.homeease",
        "display_name": "Опытная мама Даша",
        "role": UserRole.housewife,
        "lat": 55.7558,
        "lon": 37.6173,
        "is_nanny": False,
    },
    {
        "email": "mom@demo.homeease",
        "display_name": "Молодая мама Мария",
        "role": UserRole.young_mom,
        "lat": 55.76,
        "lon": 37.62,
        "is_nanny": False,
    },
    {
        "email": "nanny@demo.homeease",
        "display_name": "Няня Ольга",
        "role": UserRole.young_mom,
        "lat": 55.758,
        "lon": 37.615,
        "is_nanny": True,
    },
]

STORES = [
    {"name": "Пятёрочка", "country_code": "RU", "lat": 55.7558, "lon": 37.6173, "delivery": True},
    {"name": "Магнит", "country_code": "RU", "lat": 55.76, "lon": 37.62, "delivery": False},
    {"name": "ВкусВилл", "country_code": "RU", "lat": 55.752, "lon": 37.625, "delivery": True},
]


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _ensure_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _get_or_create_user(db, spec: dict) -> User:
    result = await db.execute(select(User).where(User.email == spec["email"]))
    user = result.scalar_one_or_none()
    if user:
        user.display_name = spec["display_name"]
        user.active_role = spec["role"]
        user.latitude = spec["lat"]
        user.longitude = spec["lon"]
        user.is_nanny = spec["is_nanny"]
        user.token_balance = 120
        return user

    user = User(
        email=spec["email"],
        password_hash=hash_password(DEMO_PASSWORD),
        display_name=spec["display_name"],
        active_role=spec["role"],
        latitude=spec["lat"],
        longitude=spec["lon"],
        is_nanny=spec["is_nanny"],
        country_code="RU",
        city="Москва",
        district="Центральный",
        token_balance=120,
    )
    db.add(user)
    await db.flush()
    for role in UserRole:
        exists = await db.execute(
            select(RoleProfile).where(RoleProfile.user_id == user.id, RoleProfile.role == role)
        )
        if not exists.scalar_one_or_none():
            db.add(RoleProfile(user_id=user.id, role=role))
    return user


async def _ensure_trial(db, user: User) -> None:
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id).order_by(Subscription.created_at.desc()).limit(1)
    )
    sub = result.scalar_one_or_none()
    now = _now()
    if sub and sub.status in (SubscriptionStatus.trialing, SubscriptionStatus.active):
        if sub.trial_end and sub.trial_end > now:
            return
        if sub.end_date and sub.end_date > now:
            return
    if not user.trial_used:
        await start_trial(db, user)
        return
    trial_end = now + timedelta(days=30)
    db.add(
        Subscription(
            user_id=user.id,
            status=SubscriptionStatus.trialing,
            plan=SubscriptionPlan.trial,
            start_date=now,
            trial_start=now,
            trial_end=trial_end,
            end_date=trial_end,
            provider="internal",
        )
    )


async def _seed_stores(db) -> None:
    existing = await db.execute(select(Store).limit(1))
    if existing.scalar_one_or_none():
        return
    for s in STORES:
        db.add(
            Store(
                name=s["name"],
                store_type=StoreType.grocery,
                latitude=s["lat"],
                longitude=s["lon"],
                country_code=s["country_code"],
                delivery_available=s["delivery"],
                delivery_radius_km=8 if s["delivery"] else None,
                district="Москва",
            )
        )


async def _clear_user_data(db, user_id: uuid.UUID) -> None:
    lists = await db.execute(select(ShoppingList.id).where(ShoppingList.user_id == user_id))
    list_ids = [row[0] for row in lists.all()]
    if list_ids:
        await db.execute(delete(ShoppingItem).where(ShoppingItem.list_id.in_(list_ids)))
    await db.execute(delete(ShoppingList).where(ShoppingList.user_id == user_id))
    await db.execute(delete(BarterAd).where(BarterAd.user_id == user_id))
    await db.execute(delete(TaskLog).where(TaskLog.user_id == user_id))
    await db.execute(delete(UserTask).where(UserTask.user_id == user_id))
    await db.execute(delete(HomeDevice).where(HomeDevice.user_id == user_id))
    await db.execute(delete(DeviceScenario).where(DeviceScenario.user_id == user_id))
    await db.execute(delete(BabyFeed).where(BabyFeed.user_id == user_id))
    await db.execute(delete(BabySleep).where(BabySleep.user_id == user_id))
    await db.execute(delete(BabyDiaper).where(BabyDiaper.user_id == user_id))
    await db.execute(delete(BabyChecklist).where(BabyChecklist.user_id == user_id))


async def _seed_housewife(db, user: User) -> None:
    await _clear_user_data(db, user.id)

    groceries = ShoppingList(user_id=user.id, name="Продукты на неделю")
    household = ShoppingList(user_id=user.id, name="Для дома")
    db.add_all([groceries, household])
    await db.flush()

    grocery_items = [
        ("Молоко", 2, "л"),
        ("Хлеб", 1, "шт"),
        ("Яйца", 10, "шт"),
        ("Курица", 1, "кг"),
    ]
    home_items = [("Стиральный порошок", 1, "уп"), ("Губки", 3, "шт")]
    for name, qty, unit in grocery_items:
        db.add(ShoppingItem(list_id=groceries.id, name=name, quantity=qty, unit=unit))
    for name, qty, unit in home_items:
        db.add(ShoppingItem(list_id=household.id, name=name, quantity=qty, unit=unit, is_bought=True))

    db.add_all(
        [
            BarterAd(
                user_id=user.id,
                title="Детские вещи 0-6 мес",
                description="Комбинезоны, почти новые",
                ad_type=BarterAdType.offer,
                category="kids",
                location_lat=user.latitude,
                location_lon=user.longitude,
            ),
            BarterAd(
                user_id=user.id,
                title="Ищу книжный шкаф",
                description="Деревянный, до 180 см",
                ad_type=BarterAdType.request,
                category="furniture",
                location_lat=user.latitude,
                location_lon=user.longitude,
            ),
        ]
    )

    cooking = UserTask(user_id=user.id, name="Готовка", default_duration_minutes=60, default_rate=500)
    cleaning = UserTask(user_id=user.id, name="Уборка", default_duration_minutes=45, default_rate=400)
    db.add_all([cooking, cleaning])
    await db.flush()

    today = date.today()
    db.add_all(
        [
            TaskLog(user_id=user.id, task_id=cooking.id, duration_minutes=60, rate=500, log_date=today),
            TaskLog(user_id=user.id, task_id=cleaning.id, duration_minutes=45, rate=400, log_date=today - timedelta(days=1)),
            TaskLog(user_id=user.id, task_id=cooking.id, duration_minutes=50, rate=500, log_date=today - timedelta(days=2)),
        ]
    )

    lamp = HomeDevice(user_id=user.id, name="Свет в гостиной", device_type="light", is_on=True)
    thermo = HomeDevice(user_id=user.id, name="Термостат", device_type="thermostat", is_on=True, value=22)
    db.add_all([lamp, thermo])
    await db.flush()

    db.add(
        DeviceScenario(
            user_id=user.id,
            name="Вечерний режим",
            actions=[
                {"device_id": str(lamp.id), "action": "on"},
                {"device_id": str(thermo.id), "action": "set_value", "value": 21},
            ],
        )
    )


async def _seed_mom(db, user: User) -> None:
    await _clear_user_data(db, user.id)
    now = _now()

    db.add_all(
        [
            BabyFeed(
                user_id=user.id,
                baby_name="Алиса",
                feed_type="breast",
                duration_minutes=20,
                feed_time=now - timedelta(hours=2),
            ),
            BabyFeed(
                user_id=user.id,
                baby_name="Алиса",
                feed_type="formula",
                volume_ml=120,
                duration_minutes=15,
                feed_time=now - timedelta(hours=6),
            ),
            BabySleep(
                user_id=user.id,
                baby_name="Алиса",
                start_time=now - timedelta(hours=10),
                end_time=now - timedelta(hours=8),
                quality=4,
            ),
            BabySleep(
                user_id=user.id,
                baby_name="Алиса",
                start_time=now - timedelta(hours=1),
                end_time=None,
                quality=None,
            ),
            BabyDiaper(user_id=user.id, baby_name="Алиса", diaper_type="wet", change_time=now - timedelta(hours=1)),
            BabyDiaper(user_id=user.id, baby_name="Алиса", diaper_type="dirty", change_time=now - timedelta(hours=4)),
        ]
    )

    checklist = [
        (0, "Кроватка", True),
        (0, "Пелёнки", True),
        (3, "Погремушка", False),
        (3, "Развивающий коврик", False),
        (6, "Стульчик для кормления", False),
    ]
    for age, name, bought in checklist:
        db.add(
            BabyChecklist(
                user_id=user.id,
                baby_name="Алиса",
                age_months=age,
                item_name=name,
                is_bought=bought,
            )
        )


async def seed() -> None:
    await _ensure_tables()
    async with async_session() as db:
        await _seed_stores(db)

        users: dict[str, User] = {}
        for spec in USERS:
            user = await _get_or_create_user(db, spec)
            await _ensure_trial(db, user)
            users[spec["email"]] = user

        await _seed_housewife(db, users["housewife@demo.homeease"])
        await _seed_mom(db, users["mom@demo.homeease"])

        await db.commit()

    print("✓ Seed complete")
    print("  Demo login: housewife@demo.homeease / demo1234")
    print("  Demo login: mom@demo.homeease / demo1234")
    print("  Nanny profile: nanny@demo.homeease / demo1234")


if __name__ == "__main__":
    asyncio.run(seed())
