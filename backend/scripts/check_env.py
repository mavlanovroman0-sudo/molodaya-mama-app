#!/usr/bin/env python3
"""
Проверка переменных окружения платёжной системы.

  cd backend
  python -m scripts.check_env
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass

PLACEHOLDER_PATTERNS = (
    re.compile(r"\.\.\.$"),
    re.compile(r"^change-me", re.I),
    re.compile(r"^your[-_]", re.I),
    re.compile(r"^ваш_", re.I),
)

COUNTRY_CODES = ("RU", "KZ", "UZ", "TJ", "GE", "KG")


@dataclass
class EnvVar:
    name: str
    required: bool = True
    pattern: re.Pattern[str] | None = None
    hint: str = ""
    providers: tuple[str, ...] = ("yookassa", "stripe", "mock")


COMMON_VARS: list[EnvVar] = [
    EnvVar("PAYMENT_PROVIDER", pattern=re.compile(r"^(yookassa|stripe|rustore|tbank|mock)$", re.I), hint="yookassa | rustore | tbank | stripe | mock"),
    EnvVar("PAYMENT_SUCCESS_URL", pattern=re.compile(r"^https?://"), hint="URL после успешной оплаты"),
    EnvVar("PAYMENT_CANCEL_URL", pattern=re.compile(r"^https?://"), hint="URL при отмене оплаты"),
    EnvVar("TRIAL_DAYS", pattern=re.compile(r"^\d+$"), hint="Дней пробного периода"),
    EnvVar("SUBSCRIPTION_ENFORCE", pattern=re.compile(r"^(true|false)$", re.I), required=False),
]

YOOKASSA_VARS: list[EnvVar] = [
    EnvVar("YOOKASSA_SHOP_ID", pattern=re.compile(r"^\d+$"), hint="shopId из личного кабинета YooKassa"),
    EnvVar(
        "YOOKASSA_SECRET_KEY",
        pattern=re.compile(r"^(test_|live_).+"),
        hint="Секретный ключ из личного кабинета YooKassa",
    ),
]

RUSTORE_VARS: list[EnvVar] = [
    EnvVar("RUSTORE_PACKAGE_NAME", hint="Package name Android-приложения", providers=("rustore",)),
    EnvVar("RUSTORE_API_KEY", hint="Public-Token RuStore API", providers=("rustore",)),
    EnvVar("RUSTORE_WEBHOOK_SECRET", hint="Ключ расшифровки webhook RuStore", providers=("rustore",)),
]

TBANK_VARS: list[EnvVar] = [
    EnvVar("TBANK_TERMINAL_KEY", hint="TerminalKey Т-Банк", providers=("tbank",)),
    EnvVar("TBANK_PASSWORD", hint="Пароль терминала Т-Банк", providers=("tbank",)),
]

STRIPE_VARS: list[EnvVar] = [
    EnvVar("STRIPE_SECRET_KEY", pattern=re.compile(r"^sk_(test|live)_"), hint="Stripe Secret key", providers=("stripe",)),
    EnvVar("STRIPE_WEBHOOK_SECRET", pattern=re.compile(r"^whsec_"), hint="Stripe webhook secret", providers=("stripe",)),
]

for cc in COUNTRY_CODES:
    STRIPE_VARS.append(
        EnvVar(
            f"STRIPE_PRICE_MONTHLY_{cc}",
            pattern=re.compile(r"^price_"),
            hint=f"Stripe Price ID monthly {cc}",
            providers=("stripe",),
            required=False,
        )
    )
    STRIPE_VARS.append(
        EnvVar(
            f"STRIPE_PRICE_YEARLY_{cc}",
            pattern=re.compile(r"^price_"),
            hint=f"Stripe Price ID yearly {cc}",
            providers=("stripe",),
            required=False,
        )
    )


def _load_env() -> dict[str, str]:
    values: dict[str, str] = dict(os.environ)
    try:
        from app.config import settings

        for field in settings.model_fields:
            val = getattr(settings, field, None)
            if val is not None:
                env_key = field.upper()
                values.setdefault(env_key, str(val))
    except Exception:
        pass

    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.isfile(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                values.setdefault(key.strip(), val.strip())

    return values


def _is_placeholder(value: str) -> bool:
    for pat in PLACEHOLDER_PATTERNS:
        if pat.search(value):
            return True
    return value in ("", "...", "sk_test_...", "whsec_...", "price_...", "test_...", "ваш_shop_id")


def check_env() -> list[str]:
    values = _load_env()
    provider = (values.get("PAYMENT_PROVIDER") or "yookassa").lower()
    problems: list[str] = []

    def _check_var(var: EnvVar) -> None:
        if provider not in var.providers and var.providers != ("yookassa", "stripe", "mock"):
            if provider not in var.providers:
                return
        raw = values.get(var.name, "")
        if not raw:
            if var.required and provider in var.providers:
                problems.append(f"❌ {var.name}: не задан. {var.hint}")
            return
        if _is_placeholder(raw):
            problems.append(f"⚠️  {var.name}: заглушка ({raw!r}). {var.hint}")
            return
        if var.pattern and not var.pattern.match(raw):
            problems.append(f"⚠️  {var.name}: неверный формат. {var.hint}")

    for var in COMMON_VARS:
        _check_var(var)

    if provider == "yookassa":
        for var in YOOKASSA_VARS:
            _check_var(var)
    elif provider == "rustore":
        for var in RUSTORE_VARS:
            _check_var(var)
    elif provider in ("tbank", "t-bank"):
        for var in TBANK_VARS:
            _check_var(var)
    elif provider == "stripe":
        for var in STRIPE_VARS:
            if var.required or values.get(var.name):
                _check_var(var)

    return problems


def main() -> int:
    values = _load_env()
    provider = values.get("PAYMENT_PROVIDER", "yookassa")
    problems = check_env()

    if not problems:
        print(f"✅ Переменные окружения OK (PAYMENT_PROVIDER={provider}).")
        return 0

    print(f"Проблемы (PAYMENT_PROVIDER={provider}):\n")
    for p in problems:
        print(f"  {p}")
    print("\nРекомендации:")
    print("  1. Заполните backend/.env (см. .env.template)")
    if provider == "yookassa":
        print("  2. python -m scripts.yookassa_setup --dry-run  # проверка конфигурации")
    print("  3. docker compose -p homeease restart backend")
    return 1


if __name__ == "__main__":
    sys.exit(main())
