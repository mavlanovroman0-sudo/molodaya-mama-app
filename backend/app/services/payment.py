"""Платёжный шлюз с абстракцией / Payment gateway abstraction."""



import logging

from abc import ABC, abstractmethod

from typing import Any

from uuid import UUID



from app.config import settings



logger = logging.getLogger(__name__)





class PaymentProvider(ABC):

    """Абстракция платёжного провайдера."""



    @abstractmethod

    async def create_checkout_session(

        self,

        user_id: UUID,

        email: str,

        price_id: str,

        country_code: str,

        plan: str,

    ) -> str:

        """Возвращает URL страницы оплаты."""



    @abstractmethod

    async def cancel_subscription(self, provider_subscription_id: str) -> bool:

        ...



    @abstractmethod

    def construct_webhook_event(self, payload: bytes, signature: str) -> dict[str, Any]:

        ...





class StripePaymentProvider(PaymentProvider):

    """Stripe (опционально, для других регионов)."""



    def __init__(self, secret_key: str | None = None):

        self._secret_key = secret_key or settings.stripe_secret_key

        self._stripe = None



    def _client(self):

        if self._stripe is None:

            import stripe



            stripe.api_key = self._secret_key

            self._stripe = stripe

        return self._stripe



    async def create_checkout_session(

        self,

        user_id: UUID,

        email: str,

        price_id: str,

        country_code: str,

        plan: str,

    ) -> str:

        stripe = self._client()

        session = stripe.checkout.Session.create(

            mode="subscription",

            customer_email=email,

            line_items=[{"price": price_id, "quantity": 1}],

            success_url=settings.payment_success_url + "?session_id={CHECKOUT_SESSION_ID}",

            cancel_url=settings.payment_cancel_url,

            metadata={

                "user_id": str(user_id),

                "country_code": country_code,

                "plan": plan,

            },

            subscription_data={"metadata": {"user_id": str(user_id), "plan": plan}},

        )

        return session.url



    async def cancel_subscription(self, provider_subscription_id: str) -> bool:

        stripe = self._client()

        try:

            stripe.Subscription.modify(provider_subscription_id, cancel_at_period_end=True)

            return True

        except Exception as e:

            logger.warning("Stripe cancel failed: %s", e)

            return False



    def construct_webhook_event(self, payload: bytes, signature: str) -> dict[str, Any]:

        stripe = self._client()

        event = stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)

        return event.to_dict() if hasattr(event, "to_dict") else dict(event)





class MockPaymentProvider(PaymentProvider):

    """Мок для тестов и dev без ключей платёжного провайдера."""



    async def create_checkout_session(

        self, user_id: UUID, email: str, price_id: str, country_code: str, plan: str

    ) -> str:

        return f"https://yookassa.ru/mock/checkout/{user_id}/{plan}"



    async def cancel_subscription(self, provider_subscription_id: str) -> bool:

        return True



    def construct_webhook_event(self, payload: bytes, signature: str) -> dict[str, Any]:

        import json



        return json.loads(payload.decode())





def get_available_payment_providers() -> list[dict[str, Any]]:
    """Список настроенных платёжных провайдеров для клиента."""
    providers: list[dict[str, Any]] = []

    from app.services.yookassa_provider import YooKassaProvider

    if YooKassaProvider().is_available():
        providers.append(
            {
                "id": "yookassa",
                "name": "YooKassa",
                "supports_cancel": True,
                "platforms": ["web", "ios", "android"],
            }
        )

    from app.services.rustore_provider import RuStoreProvider

    if RuStoreProvider().is_available():
        providers.append(
            {
                "id": "rustore",
                "name": "RuStore",
                "supports_cancel": True,
                "platforms": ["android"],
            }
        )

    from app.services.tbank_provider import TBankProvider

    if TBankProvider().is_available():
        providers.append(
            {
                "id": "tbank",
                "name": "T-Bank",
                "supports_cancel": True,
                "platforms": ["web", "ios", "android"],
            }
        )

    return providers


def get_client_payment_providers() -> list[dict[str, Any]]:
    """Провайдеры для UI: в dev возвращаем YooKassa, если ключи не настроены."""
    providers = get_available_payment_providers()
    if providers:
        return providers
    if settings.app_env.lower() != "production":
        return [
            {
                "id": "yookassa",
                "name": "YooKassa",
                "supports_cancel": True,
                "platforms": ["web", "ios", "android"],
            }
        ]
    return []


def _reject_mock_in_production(provider: str) -> None:
    if settings.app_env.lower() == "production":
        raise RuntimeError(
            f"Payment provider '{provider}' is not configured. "
            "Set real API keys; mock checkout is forbidden in production."
        )


def get_payment_provider(provider_name: str | None = None) -> PaymentProvider:
    """Выбор провайдера по PAYMENT_PROVIDER в .env или явному имени."""
    provider = (provider_name or settings.payment_provider or "yookassa").lower()

    if provider == "stripe":
        if settings.stripe_secret_key and settings.stripe_secret_key.startswith("sk_"):
            if not settings.stripe_secret_key.endswith("..."):
                return StripePaymentProvider()
        _reject_mock_in_production(provider)
        return MockPaymentProvider()

    if provider == "yookassa":
        from app.services.yookassa_provider import YooKassaPaymentProvider, YooKassaProvider

        yk = YooKassaProvider()
        if yk.is_available():
            return YooKassaPaymentProvider()
        _reject_mock_in_production(provider)
        return MockPaymentProvider()

    if provider == "rustore":
        from app.services.rustore_provider import RuStorePaymentProvider, RuStoreProvider

        rs = RuStoreProvider()
        if rs.is_available():
            return RuStorePaymentProvider()
        _reject_mock_in_production(provider)
        return MockPaymentProvider()

    if provider in ("tbank", "t-bank", "tinkoff"):
        from app.services.tbank_provider import TBankPaymentProvider, TBankProvider

        tb = TBankProvider()
        if tb.is_available():
            return TBankPaymentProvider()
        _reject_mock_in_production(provider)
        return MockPaymentProvider()

    if provider == "mock":
        _reject_mock_in_production(provider)
        return MockPaymentProvider()

    logger.warning("Unknown PAYMENT_PROVIDER=%s", provider)
    _reject_mock_in_production(provider)
    return MockPaymentProvider()





async def create_stripe_products_if_configured() -> list[str]:

    """

    Создание продуктов и цен в Stripe (legacy, только при PAYMENT_PROVIDER=stripe).

    """

    if not settings.stripe_secret_key:

        return []



    from app.config import COUNTRY_PRICING



    stripe_mod = StripePaymentProvider()._client()

    created: list[str] = []



    for cc, pricing in COUNTRY_PRICING.items():

        product = stripe_mod.Product.create(name=f"HomeEase {cc}", metadata={"country": cc})

        for plan in ("monthly", "yearly"):

            amount = pricing[plan]

            price = stripe_mod.Price.create(

                product=product.id,

                unit_amount=amount,

                currency=pricing["currency"],

                recurring={"interval": "month" if plan == "monthly" else "year"},

                metadata={"country": cc, "plan": plan},

            )

            created.append(f"{cc}_{plan}={price.id}")

            logger.info("Created Stripe price %s_%s: %s", cc, plan, price.id)



    return created


