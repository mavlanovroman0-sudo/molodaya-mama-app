# ML Models & OpenAI Prompt Registry

Документация промптов для интеграции с OpenAI.

## Модели

| Задача | Модель | Кеш TTL |
|--------|--------|---------|
| Прогноз цен | gpt-4o-mini | 1 час |
| Замена ингредиентов | gpt-4o (+ vision) | 1 час |
| Фаза сна | gpt-4o-mini | 10 мин |
| Пики кормления | gpt-4o-mini | 10 мин |
| Эмоциональный скрининг | gpt-4o-mini | 24 часа |
| Мамин комикс | gpt-4o + DALL-E | 7 дней |

## Файлы

- `backend/app/services/ai.py` — реализация и промпты
- Кеш: Redis ключ `ai:{type}:{hash}`

## Пример вызова OpenAI

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=settings.openai_api_key)
response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": PRICE_PREDICTION_PROMPT.format(language="ru")},
        {"role": "user", "content": json.dumps({"product": "молоко", "district": "Центральный"})},
    ],
    response_format={"type": "json_object"},
)
```
