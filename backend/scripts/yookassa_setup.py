#!/usr/bin/env python3
"""
Проверка и тестовый платёж YooKassa для HomeEase.

Суммы берутся из COUNTRY_PRICING (app/config.py) — не меняются.

  python -m scripts.yookassa_setup --dry-run          # проверка ключей и тарифов
  python -m scripts.yookassa_setup --create-test-payment --country RU --plan monthly
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import uuid

from app.config import COUNTRY_PRICING, settings
from app.services.yookassa_provider import YooKassaProvider, format_yookassa_amount

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def print_pricing_table() -> None:
    print("\n=== Тарифы HomeEase (COUNTRY_PRICING) ===\n")
    print(f"{'Страна':<6} {'План':<8} {'Сумма API':<14} {'Валюта':<6} Отображение")
    print("-" * 60)
    for country, pricing in COUNTRY_PRICING.items():
        for plan in ("monthly", "yearly"):
            amount = format_yookassa_amount(pricing[plan], pricing["currency"])
            display = pricing.get(f"{plan}_display", "")
            print(
                f"{country:<6} {plan:<8} {amount:<14} {pricing['currency'].upper():<6} {display}"
            )


async def run_dry_run() -> int:
    yk = YooKassaProvider()
    if not yk.is_available():
        logger.error("YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY не заданы или являются заглушками.")
        return 1

    print_pricing_table()
    print("\n✅ Ключи YooKassa заданы. Цены при оплате берутся из COUNTRY_PRICING автоматически.")
    print("   Price ID не требуются — YooKassa создаёт платёж с суммой при checkout.")
    print("\nWebhook URL: http://localhost:8001/api/v1/webhook/yookassa")
    print("Настройте в личном кабинете YooKassa → Интеграция → HTTP-уведомления")
    return 0


async def create_test_payment(country: str, plan: str) -> int:
    yk = YooKassaProvider()
    if not yk.is_available():
        logger.error("Задайте YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY в .env")
        return 1

    pricing = COUNTRY_PRICING.get(country.upper())
    if not pricing:
        logger.error("Неизвестная страна: %s", country)
        return 1

    test_user_id = uuid.uuid4()
    try:
        url = await yk.create_checkout_session(
            test_user_id,
            "test@homeease.com",
            country.upper(),
            plan,
        )
    except Exception as e:
        logger.error("Ошибка создания платежа: %s", e)
        return 1

    amount = format_yookassa_amount(pricing[plan], pricing["currency"])
    print(f"\n✅ Тестовый платёж создан")
    print(f"   Страна: {country}, план: {plan}")
    print(f"   Сумма: {amount} {pricing['currency'].upper()}")
    print(f"   URL оплаты: {url}")
    print("\nОткройте URL в браузере для тестовой оплаты (тестовая карта YooKassa).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Настройка YooKassa для HomeEase")
    parser.add_argument("--dry-run", action="store_true", help="Проверить конфигурацию и тарифы")
    parser.add_argument("--create-test-payment", action="store_true", help="Создать тестовый платёж")
    parser.add_argument("--country", default="RU", help="Код страны (RU, KZ, ...)")
    parser.add_argument("--plan", default="monthly", choices=("monthly", "yearly"))
    args = parser.parse_args()

    if args.create_test_payment:
        return asyncio.run(create_test_payment(args.country, args.plan))

    if args.dry_run or not args.create_test_payment:
        return asyncio.run(run_dry_run())

    return 0


if __name__ == "__main__":
    sys.exit(main())
