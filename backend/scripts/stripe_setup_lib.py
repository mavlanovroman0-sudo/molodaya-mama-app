"""
Логика настройки Stripe: продукт и цены по COUNTRY_PRICING из app.config.
Суммы не изменяются — только проверка и создание недостающих цен.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Protocol

from app.config import COUNTRY_PRICING

logger = logging.getLogger(__name__)

PRODUCT_NAME = "HomeEase Premium"
COUNTRY_CODES = tuple(COUNTRY_PRICING.keys())
PLANS = ("monthly", "yearly")


class StripeClient(Protocol):
    """Минимальный интерфейс Stripe API для тестов и продакшена."""

    class Product: ...

    class Price: ...


@dataclass
class PriceExpectation:
    country: str
    plan: str
    unit_amount: int
    currency: str
    interval: str
    display: str


@dataclass
class PriceCheckResult:
    country: str
    plan: str
    price_id: str | None = None
    status: str = "missing"  # ok | missing | mismatch | error
    message: str = ""
    expected_amount: int = 0
    actual_amount: int | None = None


@dataclass
class SetupReport:
    product_id: str | None = None
    product_created: bool = False
    prices: list[PriceCheckResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def env_lines(self) -> list[str]:
        lines: list[str] = []
        for r in self.prices:
            if r.price_id:
                key = f"STRIPE_PRICE_{r.plan.upper()}_{r.country}"
                lines.append(f"{key}={r.price_id}")
        return lines


def build_expectations() -> list[PriceExpectation]:
    """Ожидаемые цены из COUNTRY_PRICING (единственный источник истины)."""
    out: list[PriceExpectation] = []
    for country, pricing in COUNTRY_PRICING.items():
        for plan in PLANS:
            display_key = f"{plan}_display"
            out.append(
                PriceExpectation(
                    country=country,
                    plan=plan,
                    unit_amount=pricing[plan],
                    currency=pricing["currency"],
                    interval="month" if plan == "monthly" else "year",
                    display=pricing.get(display_key, ""),
                )
            )
    return out


def find_product_by_name(stripe_mod: Any, name: str = PRODUCT_NAME) -> dict | None:
    """Ищет активный продукт по имени."""
    for product in stripe_mod.Product.list(active=True, limit=100).auto_paging_iter():
        if product.get("name") == name:
            return product
    return None


def list_active_prices(stripe_mod: Any, product_id: str) -> list[dict]:
    prices: list[dict] = []
    for price in stripe_mod.Price.list(product=product_id, active=True, limit=100).auto_paging_iter():
        prices.append(price)
    return prices


def _price_matches(price: dict, expected: PriceExpectation) -> bool:
    if price.get("currency") != expected.currency:
        return False
    if price.get("unit_amount") != expected.unit_amount:
        return False
    recurring = price.get("recurring") or {}
    if recurring.get("interval") != expected.interval:
        return False
    return True


def find_price_for_expectation(prices: list[dict], expected: PriceExpectation) -> dict | None:
    """Ищет цену по сумме, валюте и интервалу (не по metadata)."""
    for price in prices:
        if _price_matches(price, expected):
            return price
    return None


def find_mismatched_price(prices: list[dict], expected: PriceExpectation) -> dict | None:
    """Цена с той же валютой и интервалом, но другой суммой."""
    for price in prices:
        recurring = price.get("recurring") or {}
        if price.get("currency") != expected.currency:
            continue
        if recurring.get("interval") != expected.interval:
            continue
        meta = price.get("metadata") or {}
        if meta.get("country") == expected.country and meta.get("plan") == expected.plan:
            if price.get("unit_amount") != expected.unit_amount:
                return price
    return None


def create_product(stripe_mod: Any, *, dry_run: bool) -> tuple[str | None, bool]:
    if dry_run:
        return None, False
    product = stripe_mod.Product.create(
        name=PRODUCT_NAME,
        metadata={"app": "homeease"},
    )
    return product["id"], True


def create_price(
    stripe_mod: Any,
    product_id: str,
    expected: PriceExpectation,
    *,
    dry_run: bool,
) -> str | None:
    if dry_run:
        return None
    price = stripe_mod.Price.create(
        product=product_id,
        unit_amount=expected.unit_amount,
        currency=expected.currency,
        recurring={"interval": expected.interval},
        metadata={"country": expected.country, "plan": expected.plan},
    )
    return price["id"]


def run_stripe_setup(
    stripe_mod: Any,
    *,
    dry_run: bool = False,
    create: bool = False,
) -> SetupReport:
    """
    Проверяет/создаёт продукт HomeEase Premium и цены для всех стран.
    По умолчанию только проверка; create=True — создавать недостающее.
    """
    report = SetupReport()
    expectations = build_expectations()

    product = find_product_by_name(stripe_mod)
    if product:
        report.product_id = product["id"]
        logger.info("Продукт найден: %s (%s)", PRODUCT_NAME, product["id"])
    elif create and not dry_run:
        pid, created = create_product(stripe_mod, dry_run=False)
        report.product_id = pid
        report.product_created = created
        product = {"id": pid}
        logger.info("Создан продукт: %s", pid)
    elif create and dry_run:
        logger.info("[dry-run] Будет создан продукт: %s", PRODUCT_NAME)
    else:
        report.errors.append(f'Продукт "{PRODUCT_NAME}" не найден. Запустите с --create.')
        for exp in expectations:
            report.prices.append(
                PriceCheckResult(
                    country=exp.country,
                    plan=exp.plan,
                    status="missing",
                    message="Продукт отсутствует",
                    expected_amount=exp.unit_amount,
                )
            )
        return report

    existing_prices: list[dict] = []
    if report.product_id:
        existing_prices = list_active_prices(stripe_mod, report.product_id)

    for exp in expectations:
        result = PriceCheckResult(
            country=exp.country,
            plan=exp.plan,
            expected_amount=exp.unit_amount,
        )
        matched = find_price_for_expectation(existing_prices, exp)

        if matched:
            result.price_id = matched["id"]
            result.status = "ok"
            result.message = f"OK ({exp.display})"
            report.prices.append(result)
            continue

        mismatch = find_mismatched_price(existing_prices, exp)
        if mismatch:
            result.price_id = mismatch["id"]
            result.status = "mismatch"
            result.actual_amount = mismatch.get("unit_amount")
            result.message = (
                f"Сумма в Stripe ({mismatch.get('unit_amount')}) != ожидаемой "
                f"({exp.unit_amount} {exp.currency}). Цена НЕ изменена."
            )
            report.prices.append(result)
            continue

        if create:
            try:
                if dry_run:
                    result.status = "missing"
                    result.message = f"[dry-run] Будет создана цена {exp.display}"
                else:
                    price_id = create_price(stripe_mod, report.product_id, exp, dry_run=False)
                    result.price_id = price_id
                    result.status = "ok"
                    result.message = f"Создана ({exp.display})"
                    existing_prices.append(
                        {
                            "id": price_id,
                            "unit_amount": exp.unit_amount,
                            "currency": exp.currency,
                            "recurring": {"interval": exp.interval},
                        }
                    )
            except Exception as e:
                result.status = "error"
                result.message = str(e)
                report.errors.append(f"{exp.country}/{exp.plan}: {e}")
        else:
            result.status = "missing"
            result.message = f"Отсутствует ({exp.display}). Запустите с --create."

        report.prices.append(result)

    return report


def format_report(report: SetupReport) -> str:
    lines = ["", "=== HomeEase Stripe Setup ===", ""]
    if report.product_id:
        lines.append(f"Product ID: {report.product_id}" + (" (создан)" if report.product_created else ""))
    else:
        lines.append("Product: не найден")

    lines.append("")
    lines.append(f"{'Страна':<6} {'План':<8} {'Статус':<10} Price ID / сообщение")
    lines.append("-" * 70)
    for p in report.prices:
        pid = p.price_id or "—"
        lines.append(f"{p.country:<6} {p.plan:<8} {p.status:<10} {pid}")
        if p.message:
            lines.append(f"         {p.message}")

    if report.errors:
        lines.append("")
        lines.append("Ошибки:")
        for err in report.errors:
            lines.append(f"  - {err}")

    env_lines = report.env_lines()
    if env_lines:
        lines.append("")
        lines.append("# Скопируйте в backend/.env:")
        lines.extend(env_lines)

    return "\n".join(lines)
