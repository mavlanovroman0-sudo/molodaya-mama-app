-- Миграция 003: полный набор функций / Full features migration

ALTER TABLE users ADD COLUMN IF NOT EXISTS expo_push_token TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_nanny BOOLEAN DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS shopping_lists_v2 (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) DEFAULT 'Список покупок',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS shopping_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    list_id UUID NOT NULL REFERENCES shopping_lists_v2(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    quantity DOUBLE PRECISION DEFAULT 1,
    unit VARCHAR(30),
    is_bought BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS barter_ads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    ad_type VARCHAR(20) DEFAULT 'offer',
    category VARCHAR(50),
    location_lat DOUBLE PRECISION,
    location_lon DOUBLE PRECISION,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS barter_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ad_id UUID NOT NULL REFERENCES barter_ads(id) ON DELETE CASCADE,
    from_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    to_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    jetons_amount INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    default_duration_minutes INTEGER,
    default_rate DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS task_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID REFERENCES user_tasks(id) ON DELETE SET NULL,
    duration_minutes INTEGER NOT NULL,
    rate DOUBLE PRECISION,
    log_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS home_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    device_type VARCHAR(30) DEFAULT 'light',
    is_on BOOLEAN DEFAULT FALSE,
    value DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS device_scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    actions JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS baby_feeds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    baby_name VARCHAR(100) DEFAULT 'Малыш',
    feed_type VARCHAR(20) DEFAULT 'breast',
    volume_ml INTEGER,
    duration_minutes INTEGER,
    notes TEXT,
    feed_time TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS baby_sleeps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    baby_name VARCHAR(100) DEFAULT 'Малыш',
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    quality INTEGER,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS baby_diapers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    baby_name VARCHAR(100) DEFAULT 'Малыш',
    change_time TIMESTAMPTZ DEFAULT NOW(),
    diaper_type VARCHAR(20) DEFAULT 'wet',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS baby_checklists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    baby_name VARCHAR(100) DEFAULT 'Малыш',
    age_months INTEGER DEFAULT 0,
    item_name VARCHAR(200) NOT NULL,
    is_bought BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS nanny_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    to_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shopping_lists_user ON shopping_lists_v2(user_id);
CREATE INDEX IF NOT EXISTS idx_barter_ads_active ON barter_ads(is_active);
CREATE INDEX IF NOT EXISTS idx_users_nanny ON users(is_nanny) WHERE is_nanny = TRUE;
