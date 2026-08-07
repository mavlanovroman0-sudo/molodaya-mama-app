#!/usr/bin/env python3
"""
Настройка Stripe: продукт HomeEase Premium и цены по COUNTRY_PRICING.

Использование:
  cd backend
  python -m scripts.stripe_setup              # только проверка
  python -m scripts.stripe_setup --dry-run    # проверка без создания
  python -m scripts.stripe_setup --create     # создать недостающие цены
  python -m scripts.stripe_setup --create --dry-run

Требуется STRIPE_SECRET_KEY в .env или окружении.
"""

from __future__ import annotations

import argparse
import logging
import sys

from scripts.stripe_setup_lib import format_report, run_stripe_setup

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _load_stripe_key(cli_key: str | None) -> str:
    if cli_key:
        return cli_key.strip()
    try:
        from app.config import settings

        return (settings.stripe_secret_key or "").strip()
    except Exception:
        import os

        return (os.environ.get("STRIPE_SECRET_KEY") or "").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Проверка и создание цен Stripe для HomeEase")
    parser.add_argument("--stripe-key", help="Stripe Secret Key (иначе из .env)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только показать, что будет сделано, без вызовов создания",
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="Создавать недостающий продукт и цены (по умолчанию — только проверка)",
    )
    args = parser.parse_args()

    api_key = _load_stripe_key(args.stripe_key)
    if not api_key or not api_key.startswith("sk_") or api_key.endswith("..."):
        logger.error(
            "STRIPE_SECRET_KEY не задан или является заглушкой (sk_test_...). "
            "Укажите реальный ключ в backend/.env или передайте --stripe-key."
        )
        return 1

    try:
        import stripe
    except ImportError:
        logger.error("Установите stripe: pip install stripe")
        return 1

    stripe.api_key = api_key

    try:
        report = run_stripe_setup(stripe, dry_run=args.dry_run, create=args.create)
    except Exception as e:
        logger.error("Ошибка Stripe API: %s", e)
        return 1

    print(format_report(report))

    has_problems = any(p.status in ("missing", "mismatch", "error") for p in report.prices)
    if report.errors or has_problems:
        if not args.create:
            logger.info("Подсказка: добавьте --create для создания недостающих цен.")
        return 1 if any(p.status == "error" for p in report.prices) or report.errors else 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
