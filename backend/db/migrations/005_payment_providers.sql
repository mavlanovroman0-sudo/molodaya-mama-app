-- Миграция 005: поля провайдеров платежей / Payment provider fields

ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS provider_payment_id VARCHAR(255);
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS yookassa_payment_method_id VARCHAR(255);

CREATE INDEX IF NOT EXISTS idx_subscriptions_provider_payment ON subscriptions(provider_payment_id);

-- Существующие записи: provider уже есть; NULL для новых полей по умолчанию
UPDATE subscriptions SET provider = 'yookassa' WHERE provider = 'stripe' AND status = 'active';
