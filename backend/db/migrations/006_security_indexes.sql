-- Миграция 006: уникальность платежей + индексы по user_id

-- Идемпотентность webhooks: один provider_payment_id — одна запись
CREATE UNIQUE INDEX IF NOT EXISTS uq_subscriptions_provider_payment_id
    ON subscriptions (provider_payment_id)
    WHERE provider_payment_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_barter_ads_user_id ON barter_ads (user_id);
CREATE INDEX IF NOT EXISTS idx_user_tasks_user_id ON user_tasks (user_id);
CREATE INDEX IF NOT EXISTS idx_task_logs_user_id ON task_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_home_devices_user_id ON home_devices (user_id);
CREATE INDEX IF NOT EXISTS idx_device_scenarios_user_id ON device_scenarios (user_id);
CREATE INDEX IF NOT EXISTS idx_baby_feeds_user_id ON baby_feeds (user_id);
CREATE INDEX IF NOT EXISTS idx_baby_sleeps_user_id ON baby_sleeps (user_id);
CREATE INDEX IF NOT EXISTS idx_baby_diapers_user_id ON baby_diapers (user_id);
CREATE INDEX IF NOT EXISTS idx_baby_checklists_user_id ON baby_checklists (user_id);
CREATE INDEX IF NOT EXISTS idx_nanny_requests_from ON nanny_requests (from_user_id);
CREATE INDEX IF NOT EXISTS idx_nanny_requests_to ON nanny_requests (to_user_id);
CREATE INDEX IF NOT EXISTS idx_shopping_lists_v2_user_id ON shopping_lists_v2 (user_id);
CREATE INDEX IF NOT EXISTS idx_shopping_items_list_id ON shopping_items (list_id);
