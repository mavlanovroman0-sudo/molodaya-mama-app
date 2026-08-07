"""Тесты скрипта stripe_setup (мок Stripe API)."""

from unittest.mock import MagicMock

import pytest

from app.config import COUNTRY_PRICING, settings
from scripts.stripe_setup_lib import (
    PRODUCT_NAME,
    PriceExpectation,
    _price_matches,
    build_expectations,
    find_price_for_expectation,
    format_report,
    run_stripe_setup,
)


def test_build_expectations_uses_country_pricing():
    expectations = build_expectations()
    assert len(expectations) == len(COUNTRY_PRICING) * 2
    ru_monthly = next(e for e in expectations if e.country == "RU" and e.plan == "monthly")
    assert ru_monthly.unit_amount == COUNTRY_PRICING["RU"]["monthly"]
    assert ru_monthly.currency == "rub"


def test_price_matches():
    exp = PriceExpectation("RU", "monthly", 24900, "rub", "month", "249 ₽")
    assert _price_matches(
        {"currency": "rub", "unit_amount": 24900, "recurring": {"interval": "month"}},
        exp,
    )
    assert not _price_matches(
        {"currency": "rub", "unit_amount": 19900, "recurring": {"interval": "month"}},
        exp,
    )


def test_find_price_for_expectation():
    exp = PriceExpectation("KZ", "yearly", 1000000, "kzt", "year", "10 000 ₸")
    prices = [
        {"id": "price_wrong", "currency": "kzt", "unit_amount": 125000, "recurring": {"interval": "month"}},
        {"id": "price_ok", "currency": "kzt", "unit_amount": 1000000, "recurring": {"interval": "year"}},
    ]
    found = find_price_for_expectation(prices, exp)
    assert found["id"] == "price_ok"


def test_run_stripe_setup_check_only_missing_product():
    mock_stripe = MagicMock()
    mock_stripe.Product.list.return_value.auto_paging_iter.return_value = iter([])

    report = run_stripe_setup(mock_stripe, dry_run=False, create=False)
    assert report.product_id is None
    assert len(report.prices) == 12
    assert all(p.status == "missing" for p in report.prices)


def test_run_stripe_setup_create_prices():
    mock_stripe = MagicMock()
    mock_stripe.Product.list.return_value.auto_paging_iter.return_value = iter([])
    mock_stripe.Product.create.return_value = {"id": "prod_test"}
    mock_stripe.Price.list.return_value.auto_paging_iter.return_value = iter([])
    mock_stripe.Price.create.side_effect = lambda **kw: {
        "id": f"price_{kw['metadata']['country']}_{kw['metadata']['plan']}"
    }

    report = run_stripe_setup(mock_stripe, dry_run=False, create=True)
    assert report.product_id == "prod_test"
    assert report.product_created is True
    assert mock_stripe.Price.create.call_count == 12
    assert all(p.status == "ok" for p in report.prices)
    assert "STRIPE_PRICE_MONTHLY_RU=price_RU_monthly" in format_report(report)


def test_run_stripe_setup_mismatch_warns_not_changes():
    mock_stripe = MagicMock()
    mock_stripe.Product.list.return_value.auto_paging_iter.return_value = iter(
        [{"id": "prod_1", "name": PRODUCT_NAME}]
    )
    mock_stripe.Price.list.return_value.auto_paging_iter.return_value = iter(
        [
            {
                "id": "price_bad",
                "currency": "rub",
                "unit_amount": 99900,
                "recurring": {"interval": "month"},
                "metadata": {"country": "RU", "plan": "monthly"},
            }
        ]
    )

    report = run_stripe_setup(mock_stripe, dry_run=False, create=False)
    ru_monthly = next(p for p in report.prices if p.country == "RU" and p.plan == "monthly")
    assert ru_monthly.status == "mismatch"
    assert ru_monthly.actual_amount == 99900
    mock_stripe.Price.create.assert_not_called()


def test_stripe_price_id_mapping_from_settings(monkeypatch):
    """Checkout использует Price ID из .env через settings.stripe_price_id."""
    monkeypatch.setattr(settings, "stripe_price_monthly_ru", "price_monthly_ru_test")
    monkeypatch.setattr(settings, "stripe_price_yearly_ru", "price_yearly_ru_test")

    assert settings.stripe_price_id("RU", "monthly") == "price_monthly_ru_test"
    assert settings.stripe_price_id("ru", "yearly") == "price_yearly_ru_test"
    assert settings.stripe_price_id("XX", "monthly") is None
