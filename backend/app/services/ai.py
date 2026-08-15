"""Заглушки AI с промптами для OpenAI / AI stubs with OpenAI prompt templates."""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

# --- Промпты для OpenAI (отправлять в system + user messages) ---

PRICE_PREDICTION_PROMPT = """
Ты — ИИ-скаут цен для гиперлокального приложения «молодая мама».
Проанализируй историю цен на продукт в районе пользователя.
Верни JSON: {{"product": str, "current_price": float, "predicted_low": float,
"predicted_date": str, "confidence": float, "cheaper_stores": [{{"name": str, "price": float}}],
"barter_suggestions": [str]}}
Учитывай сезонность, акции местных сетей, бартерные предложения соседей.
Язык ответа: {language}
"""

INGREDIENT_SUBSTITUTE_PROMPT = """
Ты — глобальный переводчик ингредиентов «Вкус мира».
Пользователь прислал фото/описание продукта из другой кухни.
Найди локальные аналоги в магазинах региона {region}.
Верни JSON: {{"original": str, "substitutes": [{{"name": str, "store": str, "price_range": str,
"conversion_ratio": str}}], "recipe_tip": str}}
Язык: {language}
"""

SLEEP_PHASE_PROMPT = """
Ты — консультант по детскому сну. На основе логов сна младенца предскажи фазу.
Данные: возраст {age_months} мес., последние сны: {sleep_logs}
Верни JSON: {{"current_phase": "light"|"deep"|"rem"|"awake", "confidence": float,
"next_wake_window": str (ISO), "recommendation": str}}
Язык: {language}
"""

FEEDING_PEAK_PROMPT = """
Проанализируй график кормлений и предупреди о «вечернем безумии».
Логи: {feeding_logs}, возраст: {age_months} мес.
Верни JSON: {{"next_peak_at": str, "evening_chaos_warning": bool, "interval_hours_avg": float,
"message": str}}
Язык: {language}
"""


def _cache_key(prefix: str, payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    return f"ai:{prefix}:{hashlib.sha256(raw.encode()).hexdigest()[:32]}"


async def get_cached_or_compute(
    redis_client: Any,
    key: str,
    ttl_seconds: int,
    compute_fn,
) -> dict:
    """Кеш AI-ответов в Redis."""
    if redis_client:
        cached = await redis_client.get(key)
        if cached:
            return json.loads(cached)
    result = await compute_fn()
    if redis_client:
        await redis_client.setex(key, ttl_seconds, json.dumps(result, default=str))
    return result


async def predict_price(
    product: str,
    district: str,
    language: str = "ru",
    redis_client: Any = None,
) -> dict:
    """
    ИИ-скаут «Где дешевле».
    OpenAI: model=gpt-4o-mini, system=PRICE_PREDICTION_PROMPT.format(language=language),
    user={{"product": product, "district": district}}
    Кеш: 1 час
    """
    key = _cache_key("price", {"product": product, "district": district})

    async def compute():
        # Заглушка без реального API-ключа
        return {
            "product": product,
            "current_price": 199.0,
            "predicted_low": 149.0,
            "predicted_date": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
            "confidence": 0.72,
            "cheaper_stores": [{"name": "Пятёрочка", "price": 159.0}],
            "barter_suggestions": ["Обменяйте излишки муки на яйца в бартере района"],
            "_prompt_hint": PRICE_PREDICTION_PROMPT.format(language=language),
        }

    return await get_cached_or_compute(redis_client, key, 3600, compute)


async def substitute_ingredient(
    description: str,
    region: str,
    language: str = "ru",
    redis_client: Any = None,
) -> dict:
    """
    «Вкус мира» — замена ингредиентов.
    OpenAI vision если есть фото; иначе text.
    Кеш: 1 час
    """
    key = _cache_key("ingredient", {"description": description, "region": region})

    async def compute():
        return {
            "original": description,
            "substitutes": [
                {"name": "Сметана 20%", "store": "Магнит", "price_range": "80-95₽", "conversion_ratio": "1:1"},
            ],
            "recipe_tip": "Для кремовой текстуры добавьте 1 ч.л. крахмала",
            "_prompt_hint": INGREDIENT_SUBSTITUTE_PROMPT.format(region=region, language=language),
        }

    return await get_cached_or_compute(redis_client, key, 3600, compute)


async def predict_sleep_phase(
    age_months: int,
    sleep_logs: list[dict],
    language: str = "ru",
    redis_client: Any = None,
) -> dict:
    """
    Прогноз фазы сна ребёнка.
    Кеш: 10 минут
    """
    key = _cache_key("sleep", {"age": age_months, "logs": sleep_logs[-5:]})

    async def compute():
        return {
            "current_phase": "light",
            "confidence": 0.68,
            "next_wake_window": (datetime.now(timezone.utc) + timedelta(minutes=45)).isoformat(),
            "recommendation": "Оптимальное время для укладывания через 30-45 минут",
            "_prompt_hint": SLEEP_PHASE_PROMPT.format(
                age_months=age_months, sleep_logs=json.dumps(sleep_logs), language=language
            ),
        }

    return await get_cached_or_compute(redis_client, key, 600, compute)


async def predict_feeding_peaks(
    age_months: int,
    feeding_logs: list[dict],
    language: str = "ru",
    redis_client: Any = None,
) -> dict:
    """Прогноз пиков кормления / evening chaos warning. Кеш: 10 мин."""
    key = _cache_key("feeding", {"age": age_months, "logs": feeding_logs[-10:]})

    async def compute():
        now = datetime.now(timezone.utc)
        evening = now.hour >= 17
        return {
            "next_peak_at": (now + timedelta(hours=2.5)).isoformat(),
            "evening_chaos_warning": evening,
            "interval_hours_avg": 2.8,
            "message": "Вечерний пик близко — подготовьте тихую зону",
            "_prompt_hint": FEEDING_PEAK_PROMPT.format(
                feeding_logs=json.dumps(feeding_logs), age_months=age_months, language=language
            ),
        }

    return await get_cached_or_compute(redis_client, key, 600, compute)
