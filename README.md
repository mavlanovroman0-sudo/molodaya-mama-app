# HomeEase 2.0

Кроссплатформенное супер-приложение для домохозяек и молодых мам (React Native + Expo, FastAPI, PostgreSQL).

## Быстрый старт

```bash
# Скопировать переменные окружения
cp backend/.env.example backend/.env

# Запуск всего стека
# Флаг -p обязателен, если папка проекта с кириллицей в пути
docker compose -p homeease up --build

# Или локально:
# Backend
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npx expo start --web
```

> **Локали:** после правок `i18n/locales.json` скопируйте файл в `frontend/src/i18n/locales.json`.

## Сервисы

| Сервис      | URL                          |
|-------------|------------------------------|
| API         | http://localhost:8000        |
| Swagger UI  | http://localhost:8000/docs   |
| Frontend    | http://localhost:8081        |
| BLE mock    | http://localhost:8100        |

## Структура монорепозитория

```
├── frontend/       # React Native + Expo (iOS, Android, Web)
├── backend/        # FastAPI + PostgreSQL + Redis
├── ble-service/    # BLE брелок «Красная кнопка» (mock)
├── ml-models/      # Заглушки и промпты для OpenAI
├── i18n/           # Локали (ru, kk, uz, tg, ka, ky)
└── docker-compose.yml
```

## Роли

- **Домохозяйка** — бюджет, закупки, бартер, умный дом, подписки
- **Молодая мама** — трекер малыша, сон, кормление, экстренная помощь

Общие данные: жетоны, избранные магазины, устройства умного дома, доставка.

## Seed-данные магазинов

```bash
# PostgreSQL должен быть запущен (docker compose -p homeease up postgres -d)
cd backend
# Linux/macOS:
DATABASE_URL=postgresql+asyncpg://homeease:homeease_dev@localhost:5432/homeease python -m scripts.seed_stores
# Windows PowerShell:
$env:DATABASE_URL="postgresql+asyncpg://homeease:homeease_dev@localhost:5432/homeease"; python -m scripts.seed_stores
```

Скрипт очищает таблицу `stores` и заполняет 12 тестовых магазинов (по 2 на каждую из 6 стран).

## Реферальная система

Каждый пользователь получает уникальный код (`POST /api/v1/referral/generate`). Новый пользователь применяет код (`POST /api/v1/referral/apply`) — пригласивший получает **50 жетонов**, новичок **20** (настраивается в `.env`).

### Миграция

```bash
psql -U homeease -d homeease -f backend/db/migrations/002_referrals.sql
# или в Docker:
docker compose -p homeease exec postgres psql -U homeease -d homeease -f /docker-entrypoint-initdb.d/../migrations/002_referrals.sql
```

Проще из хоста:

```bash
docker compose -p homeease exec -T postgres psql -U homeease -d homeease < backend/db/migrations/002_referrals.sql
```

### API

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/referral/generate` | Получить/создать код |
| POST | `/api/v1/referral/apply` | Применить код |
| GET | `/api/v1/referral/stats` | Статистика приглашений |

### Push-напоминания

- **APScheduler** внутри API (ежедневно в 10:00 UTC) — `ENABLE_SCHEDULER=true`
- **Celery Beat** (опционально): `celery -A celery_app beat` и `celery -A celery_app worker`
- **Cron вручную**: `POST /api/v1/internal/cron/invite-reminder` с заголовком `X-Cron-Secret: <CRON_SECRET>`

### Remote Config (MVP)

`GET /api/v1/config/remote` → `{ "show_invite_banner": true }` (фронтенд использует вместо Firebase в Expo).

## Тесты

```bash
cd backend && pytest
# или в Docker:
docker compose -p homeease run --rm --no-deps backend pytest tests/ -v

cd frontend && npm test
```

## Подписка и YooKassa

HomeEase 2.0 работает по модели **платной подписки**. Платёжный провайдер по умолчанию — **YooKassa** (`PAYMENT_PROVIDER=yookassa`). Альтернативы: **RuStore** (`rustore`), **Т-Банк** (`tbank`). Stripe остаётся опциональным (`PAYMENT_PROVIDER=stripe`).

Новым пользователям при регистрации автоматически выдаётся **пробный период 14 дней**.

### Тарифы (месяц / год)

| Страна | Месяц | Год |
|--------|-------|-----|
| Россия | 249 ₽ | 1990 ₽ |
| Казахстан | 1250 ₸ | 10 000 ₸ |
| Узбекистан | 24 500 soʻm | 196 000 soʻm |
| Таджикистан | 25 сомони | 200 сомони |
| Грузия | 9 GEL | 72 GEL |
| Киргизия | 120 сом | 960 сом |

Источник истины — `backend/app/config.py` → `COUNTRY_PRICING`. YooKassa создаёт платёж с этой суммой при checkout (Price ID не нужны).

### Настройка YooKassa (автоматизированная)

```bash
cd backend

# 1. Заполните .env: YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY, PAYMENT_PROVIDER=yookassa
cp .env.template .env

# 2. Проверка переменных
python -m scripts.check_env

# 3. Проверка тарифов и ключей
python -m scripts.yookassa_setup --dry-run

# 4. Тестовый платёж (опционально)
python -m scripts.yookassa_setup --create-test-payment --country RU --plan monthly

# 5. Перезапуск бэкенда
docker compose -p homeease restart backend

# 6. Тест webhook
python -m scripts.test_webhook --email test@homeease.com --password Test1234
```

В Docker:

```bash
docker compose -p homeease exec -T backend python -m scripts.check_env
docker compose -p homeease exec -T backend python -m scripts.yookassa_setup --dry-run
```

### Регистрация в YooKassa (вручную)

1. Регистрация: [https://yookassa.ru](https://yookassa.ru) → подключить магазин.
2. **Интеграция → Ключи API** → скопировать `shopId` и секретный ключ (тестовый `test_...`).
3. В `backend/.env`:
   ```env
   PAYMENT_PROVIDER=yookassa
   YOOKASSA_SHOP_ID=123456
   YOOKASSA_SECRET_KEY=test_xxxxxxxx
   PAYMENT_SUCCESS_URL=http://localhost:8081/subscription/success
   PAYMENT_CANCEL_URL=http://localhost:8081/subscription/cancel
   ```
4. **HTTP-уведомления (webhook)** в личном кабинете:
   - URL: `https://ваш-домен/api/v1/webhook/yookassa`
   - Локально: проброс через ngrok или туннель на `http://localhost:8001/api/v1/webhook/yookassa`
   - События: `payment.succeeded`, `payment.canceled`, `payment.waiting_for_capture`
5. Перезапуск: `docker compose -p homeease restart backend`

### Stripe (опционально)

Для `PAYMENT_PROVIDER=stripe` используйте legacy-скрипт `scripts/stripe_setup.py` и webhook `/api/v1/webhook/stripe`. См. `backend/.env.example` для `STRIPE_PRICE_*`.

### RuStore (альтернатива, Android)

RuStore используется для in-app подписок через RuStore Pay SDK. Бэкенд возвращает deep link `homeease://rustore-pay?...`, мобильное приложение открывает RuStore Pay.

**Регистрация и ключи:**

1. Зарегистрируйте аккаунт разработчика: [https://www.rustore.ru/developer](https://www.rustore.ru/developer).
2. Создайте приложение в RuStore Console, укажите package name (например `com.homeease.app`).
3. В разделе **Монетизация → Подписки** создайте продукты `homeease_monthly` и `homeease_yearly` (или свои ID).
4. **API-ключи** → скопируйте Public-Token для Public API v4.
5. **Webhooks** → получите секретный ключ для расшифровки AES-256-GCM payload.

В `backend/.env`:

```env
PAYMENT_PROVIDER=rustore
RUSTORE_PACKAGE_NAME=com.homeease.app
RUSTORE_API_KEY=ваш_public_token
RUSTORE_WEBHOOK_SECRET=ваш_32_байтный_ключ
RUSTORE_SANDBOX=true
RUSTORE_PRODUCT_MONTHLY=homeease_monthly
RUSTORE_PRODUCT_YEARLY=homeease_yearly
```

**Webhook:**

- URL: `https://ваш-домен/api/v1/webhook/rustore`
- Локально: туннель на `http://localhost:8001/api/v1/webhook/rustore`
- События: `ACTIVATED`, `RENEWED`, `CANCELLED`, `CLOSED`, `PAYMENT_FAILED`
- Payload приходит зашифрованным в поле `payload`; бэкенд расшифровывает через `RUSTORE_WEBHOOK_SECRET`.

Проверка: `python -m scripts.check_env` (при `PAYMENT_PROVIDER=rustore`).

### Т-Банк (альтернатива)

Интернет-эквайринг Т-Банка (Tinkoff Acquiring). Суммы берутся из `COUNTRY_PRICING` (в копейках/тиынах).

**Регистрация и ключи:**

1. Подключите интернет-эквайринг: [https://www.tbank.ru/kassa/](https://www.tbank.ru/kassa/).
2. В личном кабинете получите **TerminalKey** и **Пароль** терминала.
3. Для тестов используйте демо-терминал из [документации API](https://www.tbank.ru/kassa/dev/).

В `backend/.env`:

```env
PAYMENT_PROVIDER=tbank
TBANK_TERMINAL_KEY=ваш_terminal_key
TBANK_PASSWORD=ваш_пароль
TBANK_API_URL=https://securepay.tinkoff.ru/v2
PAYMENT_SUCCESS_URL=http://localhost:8081/subscription/success
PAYMENT_CANCEL_URL=http://localhost:8081/subscription/cancel
```

**Webhook (уведомления):**

- URL: `https://ваш-домен/api/v1/webhook/tbank`
- Локально: туннель на `http://localhost:8001/api/v1/webhook/tbank`
- В кабинете Т-Банка включите уведомления на этот URL.
- Подпись проверяется по полю `Token` (SHA-256 от отсортированных параметров + пароль).

Checkout через API: `POST /api/v1/subscription/checkout` с телом `{"plan": "monthly", "provider": "tbank"}` (поле `provider` опционально, если задан `PAYMENT_PROVIDER`).

### Миграция подписки

```bash
docker compose -p homeease exec -T postgres psql -U homeease -d homeease < backend/db/migrations/004_subscription.sql
docker compose -p homeease exec -T postgres psql -U homeease -d homeease < backend/db/migrations/005_payment_providers.sql
```

### API подписки

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/v1/user/subscription-status` | Статус, оставшиеся дни, цены |
| POST | `/api/v1/subscription/checkout` | Создать платёж (`plan`: `monthly` / `yearly`, опционально `provider`: `yookassa` / `rustore` / `tbank`) |
| POST | `/api/v1/subscription/cancel` | Отмена в конце периода |
| POST | `/api/v1/webhook/yookassa` | Webhook YooKassa |
| POST | `/api/v1/webhook/rustore` | Webhook RuStore |
| POST | `/api/v1/webhook/tbank` | Webhook Т-Банк |
| POST | `/api/v1/webhook/stripe` | Webhook Stripe (только при PAYMENT_PROVIDER=stripe) |

Без активной подписки или пробного периода защищённые эндпоинты возвращают **403** с `code: "payment_required"`. Исключения: `/auth`, `/webhook`, `/health`, `/geo`, `/config`, эндпоинты подписки.

Для отключения проверки в dev: `SUBSCRIPTION_ENFORCE=false`.

## Настройка продакшена

### 1. Переменные окружения

```bash
cp backend/.env.example backend/.env.production
# Заполните секреты:
#   openssl rand -hex 32   → JWT_SECRET, CRON_SECRET
```

Обязательно для production:

| Переменная | Значение |
|------------|----------|
| `APP_ENV` | `production` |
| `SUBSCRIPTION_ENFORCE` | `true` |
| `JWT_SECRET` | случайная строка (`openssl rand -hex 32`) |
| `CRON_SECRET` | случайная строка |
| `CORS_ORIGINS` | `https://ваш-домен,https://www.ваш-домен` |
| `POSTGRES_PASSWORD` | надёжный пароль БД |
| `YOOKASSA_SHOP_ID` / `YOOKASSA_SECRET_KEY` | из личного кабинета YooKassa |
| `PAYMENT_SUCCESS_URL` | `https://app.домен/subscription/success` или `homeease://payment/success` |
| `SENTRY_DSN` | опционально, см. [sentry.io](https://sentry.io) |

### 2. Сборка и запуск (Docker)

```bash
# Сборка production-образов
docker compose -f docker-compose.prod.yml --env-file backend/.env.production build

# Запуск
docker compose -f docker-compose.prod.yml --env-file backend/.env.production up -d

# Миграции БД
docker compose -f docker-compose.prod.yml exec backend bash scripts/migrate.sh

# Проверка готовности
curl http://localhost/health/ready
# → {"status":"ready","database":"ok"}
```

Backend в production: **gunicorn** + 4 **uvicorn** workers (`backend/Dockerfile.prod`), JSON-логирование, без `--reload`.

### 3. SSL и домен (nginx + Let's Encrypt)

1. Укажите домен в `docs/nginx-homeease.example.conf` (замените `YOUR_DOMAIN`).
2. Получите сертификат:
   ```bash
   certbot certonly --standalone -d your-domain.com -d www.your-domain.com
   cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docs/ssl/
   cp /etc/letsencrypt/live/your-domain.com/privkey.pem docs/ssl/
   ```
3. Раскомментируйте HTTPS-блок в nginx-конфиге.
4. `docker compose -f docker-compose.prod.yml restart nginx`

Альтернатива: **Traefik** или **Caddy** с автоматическим HTTPS.

### 4. Мониторинг (Sentry)

- Backend: задайте `SENTRY_DSN` в `.env.production` — инициализация только при `APP_ENV=production`.
- Frontend: `EXPO_PUBLIC_SENTRY_DSN` в `frontend/.env` или EAS secrets.
- Получение DSN: Sentry → Create Project → Client Keys (DSN).

### 5. Мобильная сборка (EAS)

```bash
cd frontend
npm install -g eas-cli
eas login
eas build:configure   # один раз
eas build --platform android --profile production   # AAB для Google Play / RuStore
eas build --platform ios --profile production
```

Конфигурация: `frontend/eas.json`, идентификаторы: `frontend/app.config.js`.

Deep links: `homeease://payment/success`, `homeease://payment/cancel`.

### 6. Webhook YooKassa (production)

- URL: `https://ваш-домен/api/v1/webhook/yookassa`
- События: `payment.succeeded`, `payment.canceled`, `payment.waiting_for_capture`
- Проверка: `python -m scripts.test_webhook --email test@example.com --password Test1234`

### 7. Документация

| Файл | Описание |
|------|----------|
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | Руководство пользователя |
| [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) | Чек-лист ручного тестирования |
| [docs/nginx-homeease.example.conf](docs/nginx-homeease.example.conf) | Пример nginx |
| Юридические документы | В приложении: Профиль / Регистрация → Политика и Условия |

### 8. Миграции на продакшене

Все SQL-файлы из `backend/db/migrations/` применяются скриптом `backend/scripts/migrate.sh` в алфавитном порядке:

```bash
# В контейнере production
docker compose -f docker-compose.prod.yml exec backend bash scripts/migrate.sh

# Или вручную один файл
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U homeease -d homeease < backend/db/migrations/004_subscription.sql
```
