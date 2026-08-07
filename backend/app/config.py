"""Конфигурация приложения / Application settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


# Цены в минимальных единицах валюты для Stripe / Prices in minor units
COUNTRY_PRICING: dict[str, dict] = {
    "RU": {"currency": "rub", "monthly": 24900, "yearly": 199000, "monthly_display": "249 ₽", "yearly_display": "1990 ₽"},
    "KZ": {"currency": "kzt", "monthly": 125000, "yearly": 1000000, "monthly_display": "1250 ₸", "yearly_display": "10 000 ₸"},
    "UZ": {"currency": "uzs", "monthly": 24500, "yearly": 196000, "monthly_display": "24 500 soʻm", "yearly_display": "196 000 soʻm"},
    "TJ": {"currency": "tjs", "monthly": 2500, "yearly": 20000, "monthly_display": "25 сомони", "yearly_display": "200 сомони"},
    "GE": {"currency": "gel", "monthly": 900, "yearly": 7200, "monthly_display": "9 GEL", "yearly_display": "72 GEL"},
    "KG": {"currency": "kgs", "monthly": 12000, "yearly": 96000, "monthly_display": "120 сом", "yearly_display": "960 сом"},
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://homeease:homeease_dev@localhost:5432/homeease"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    openai_api_key: str = ""
    cors_origins: str = "http://localhost:8081,http://localhost:19006"
    ip_geo_api_url: str = "http://ip-api.com/json"

    referral_bonus_referrer: int = 50
    referral_bonus_referee: int = 20
    cron_secret: str = "change-me-cron-secret"
    fcm_server_key: str = ""
    enable_scheduler: bool = True
    app_env: str = "development"  # development | production
    sentry_dsn: str = ""

    # Подписка / Subscription
    trial_days: int = 14
    subscription_enforce: bool = True
    payment_provider: str = "yookassa"

    # YooKassa (основной провайдер)
    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""

    # RuStore (альтернатива, Android)
    rustore_app_id: str = ""
    rustore_package_name: str = ""
    rustore_api_key: str = ""
    rustore_webhook_secret: str = ""
    rustore_sandbox: bool = True
    rustore_product_monthly: str = "homeease_monthly"
    rustore_product_yearly: str = "homeease_yearly"

    # Т-Банк / Tinkoff Acquiring (альтернатива)
    tbank_terminal_key: str = ""
    tbank_password: str = ""
    tbank_api_url: str = "https://securepay.tinkoff.ru/v2"

    # URL возврата после оплаты (общие для всех провайдеров)
    payment_success_url: str = "http://localhost:8081/subscription/success"
    payment_cancel_url: str = "http://localhost:8081/subscription/cancel"

    # Stripe (опционально, PAYMENT_PROVIDER=stripe)
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_success_url: str = "http://localhost:8081/subscription/success"
    stripe_cancel_url: str = "http://localhost:8081/subscription/cancel"

    # Stripe Price IDs (создать в Dashboard / create in Stripe Dashboard)
    stripe_price_monthly_ru: str = ""
    stripe_price_yearly_ru: str = ""
    stripe_price_monthly_kz: str = ""
    stripe_price_yearly_kz: str = ""
    stripe_price_monthly_uz: str = ""
    stripe_price_yearly_uz: str = ""
    stripe_price_monthly_tj: str = ""
    stripe_price_yearly_tj: str = ""
    stripe_price_monthly_ge: str = ""
    stripe_price_yearly_ge: str = ""
    stripe_price_monthly_kg: str = ""
    stripe_price_yearly_kg: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def stripe_price_id(self, country_code: str, plan: str) -> str | None:
        """Получить Stripe Price ID по стране и плану."""
        cc = country_code.upper()
        key = f"stripe_price_{plan}_{cc.lower()}"
        val = getattr(self, key, "")
        return val or None


def validate_production_secrets() -> None:
    """Завершить процесс при дефолтных/пустых секретах в production."""
    if settings.app_env.lower() != "production":
        return
    problems: list[str] = []
    if settings.jwt_secret in ("dev-secret", "change-me-in-production", ""):
        problems.append("JWT_SECRET")
    if settings.cron_secret in ("change-me-cron-secret", "change-me", ""):
        problems.append("CRON_SECRET")
    if "homeease_dev" in settings.database_url or settings.database_url.endswith("@localhost:5432/homeease"):
        problems.append("DATABASE_URL (default/dev credentials)")
    origins = settings.cors_origin_list
    if not origins or "*" in origins:
        problems.append("CORS_ORIGINS (non-empty list of explicit origins, not '*')")
    provider = (settings.payment_provider or "").lower()
    if provider == "yookassa" and (
        not settings.yookassa_shop_id or not settings.yookassa_secret_key
    ):
        problems.append("YOOKASSA_SHOP_ID / YOOKASSA_SECRET_KEY")
    elif provider == "stripe" and not (
        settings.stripe_secret_key.startswith("sk_")
        and not settings.stripe_secret_key.endswith("...")
    ):
        problems.append("STRIPE_SECRET_KEY")
    elif provider == "rustore" and (
        not settings.rustore_api_key or not settings.rustore_webhook_secret
    ):
        problems.append("RUSTORE_API_KEY / RUSTORE_WEBHOOK_SECRET")
    elif provider in ("tbank", "t-bank", "tinkoff") and (
        not settings.tbank_terminal_key or not settings.tbank_password
    ):
        problems.append("TBANK_TERMINAL_KEY / TBANK_PASSWORD")
    elif provider == "mock":
        problems.append("PAYMENT_PROVIDER (mock запрещён в production)")
    if not settings.payment_success_url or "localhost" in settings.payment_success_url:
        problems.append("PAYMENT_SUCCESS_URL (production URL, not localhost)")
    if not settings.payment_cancel_url or "localhost" in settings.payment_cancel_url:
        problems.append("PAYMENT_CANCEL_URL (production URL, not localhost)")
    if problems:
        raise ValueError(
            f"Production requires secure secrets. Set: {', '.join(problems)}"
        )


settings = Settings()
validate_production_secrets()
