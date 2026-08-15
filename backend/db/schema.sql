-- HomeEase 2.0 — PostgreSQL Schema
-- Схема БД: единый аккаунт, две роли, общие и ролевые данные

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Языки интерфейса
CREATE TYPE app_language AS ENUM ('ru', 'kk', 'uz', 'tg', 'ka', 'ky');
CREATE TYPE user_role AS ENUM ('housewife', 'young_mom');
CREATE TYPE store_type AS ENUM ('grocery', 'household', 'pharmacy', 'baby', 'restaurant', 'cafe');
CREATE TYPE device_protocol AS ENUM ('matter', 'zigbee', 'home_assistant', 'yandex', 'google', 'homekit');
CREATE TYPE barter_status AS ENUM ('open', 'matched', 'completed', 'cancelled');

-- Пользователи / Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    phone VARCHAR(20),
    -- Текущая активная роль / Active role view
    active_role user_role DEFAULT 'housewife',
    -- Локализация / Localization
    language app_language DEFAULT 'ru',
    auto_detect_language BOOLEAN DEFAULT TRUE,
    -- Геолокация (анонимизированная для бартера) / Geo
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    district VARCHAR(200),          -- район / district
    microdistrict VARCHAR(200),     -- микрорайон
    city VARCHAR(100),
    country_code CHAR(2) DEFAULT 'RU',
    address_manual TEXT,
  -- Жетоны — внутренняя валюта / Internal tokens
    token_balance INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_district ON users(district);
CREATE INDEX idx_users_country ON users(country_code);

-- Ролевые настройки (специфичные данные) / Role-specific settings
CREATE TABLE role_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role user_role NOT NULL,
    settings JSONB DEFAULT '{}',
    dashboard_layout JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, role)
);

-- Магазины / Stores
CREATE TABLE stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    store_type store_type NOT NULL,
    address TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    district VARCHAR(200),
    country_code CHAR(2) DEFAULT 'RU',
    delivery_available BOOLEAN DEFAULT FALSE,
    delivery_radius_km INTEGER DEFAULT 5,
    delivery_api_url TEXT,
    website_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_stores_district ON stores(district);
CREATE INDEX idx_stores_type ON stores(store_type);

-- Избранные магазины / Favorite stores
CREATE TABLE favorite_stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, store_id)
);

-- Слоты доставки (кеш) / Delivery slots cache
CREATE TABLE delivery_slots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    slot_start TIMESTAMPTZ NOT NULL,
    slot_end TIMESTAMPTZ NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    price_estimate DECIMAL(10,2),
    cached_at TIMESTAMPTZ DEFAULT NOW()
);

-- Корзины доставки / Delivery baskets
CREATE TABLE delivery_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'draft',
    total_amount DECIMAL(12,2),
    stores_breakdown JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Устройства умного дома / Smart home devices
CREATE TABLE smart_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    room VARCHAR(50),
    device_type VARCHAR(50),  -- light, thermostat, lock, kettle, noise_machine
    protocol device_protocol NOT NULL,
    external_id VARCHAR(255),
    provider_config JSONB DEFAULT '{}',
    is_online BOOLEAN DEFAULT FALSE,
    last_state JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Сценарии умного дома / Automation scenarios
CREATE TABLE home_scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role user_role NOT NULL,
    name VARCHAR(100) NOT NULL,
    trigger_type VARCHAR(50),
    actions JSONB NOT NULL DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Настройки автомобиля / Vehicle settings
CREATE TABLE vehicle_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    make VARCHAR(50),
    model VARCHAR(50),
    integration_type VARCHAR(50),  -- carplay, android_auto, obd, tesla_api
    api_config JSONB DEFAULT '{}',
    child_mode_enabled BOOLEAN DEFAULT FALSE,
    fuel_reminder_km INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- BLE брелок «Красная кнопка» / Red button keychain
CREATE TABLE ble_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_mac VARCHAR(17) UNIQUE,
    nickname VARCHAR(50) DEFAULT 'Красная кнопка',
    last_seen_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- === Профиль «Домохозяйка» ===

-- Бартер / Barter exchange
CREATE TABLE barters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    district VARCHAR(200),
    status barter_status DEFAULT 'open',
    tokens_offered INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Банковские транзакции (временный анализ) / Subscription hunter
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(12,2),
    merchant VARCHAR(200),
    category VARCHAR(100),
    is_subscription BOOLEAN DEFAULT FALSE,
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Стресс / Anti-burnout
CREATE TABLE stress_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score INTEGER CHECK (score BETWEEN 1 AND 10),
    source VARCHAR(50),  -- manual, healthkit, watch
    notes TEXT,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Невидимая зарплата — сэкономленные часы/деньги
CREATE TABLE invisible_salary_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    period_start DATE,
    period_end DATE,
    money_saved DECIMAL(12,2),
    hours_saved DECIMAL(8,2),
    breakdown JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Списки покупок
CREATE TABLE shopping_lists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) DEFAULT 'Список покупок',
    items JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- === Профиль «Молодая мама» ===

-- Профили детей
CREATE TABLE babies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    gender VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Логи кормления / Feeding logs
CREATE TABLE feeding_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    baby_id UUID NOT NULL REFERENCES babies(id) ON DELETE CASCADE,
    feeding_type VARCHAR(20),  -- breast, bottle, solid
    duration_minutes INTEGER,
    amount_ml INTEGER,
    side VARCHAR(10),
    notes TEXT,
    logged_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_feeding_baby_time ON feeding_logs(baby_id, logged_at DESC);

-- Трекер сна / Sleep tracking
CREATE TABLE sleep_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    baby_id UUID NOT NULL REFERENCES babies(id) ON DELETE CASCADE,
    sleep_start TIMESTAMPTZ NOT NULL,
    sleep_end TIMESTAMPTZ,
    quality VARCHAR(20),
    phase_prediction VARCHAR(50),  -- AI: light, deep, rem
  notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Подгузники / Diaper logs
CREATE TABLE diaper_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    baby_id UUID NOT NULL REFERENCES babies(id) ON DELETE CASCADE,
    diaper_type VARCHAR(20),  -- wet, dirty, both
    logged_at TIMESTAMPTZ DEFAULT NOW()
);

-- Голосовой дневник развития
CREATE TABLE baby_development_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    baby_id UUID NOT NULL REFERENCES babies(id) ON DELETE CASCADE,
    voice_transcript TEXT,
    milestones JSONB DEFAULT '[]',
    pdf_url TEXT,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Эмоциональный компас (ПРД скрининг)
CREATE TABLE emotional_screenings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score INTEGER,
    answers JSONB,
    support_offered BOOLEAN DEFAULT FALSE,
    screened_at TIMESTAMPTZ DEFAULT NOW()
);

-- Партнёрские челленджи
CREATE TABLE partner_challenges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mission TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    tokens_reward INTEGER DEFAULT 5,
    due_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI кеш / AI response cache
CREATE TABLE ai_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    response JSONB NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ai_cache_expires ON ai_cache(expires_at);

-- Обновление updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER delivery_orders_updated_at BEFORE UPDATE ON delivery_orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
