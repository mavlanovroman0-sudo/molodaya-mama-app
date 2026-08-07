#!/usr/bin/env python3
"""Проверка статуса подписки через API / Check subscription status via API.

Примеры:
  python -m scripts.check_subscription test@homeease.com Test1234
  API_URL=http://localhost:8001 python -m scripts.check_subscription test@homeease.com Test1234
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import httpx

DEFAULT_API_URL = os.environ.get("API_URL", "http://localhost:8001")


def login(client: httpx.Client, email: str, password: str) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    if resp.status_code != 200:
        print(f"Ошибка входа ({resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)
    return resp.json()["access_token"]


def fetch_status(client: httpx.Client, token: str) -> dict:
    resp = client.get(
        "/api/v1/user/subscription-status",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code != 200:
        print(f"Ошибка статуса ({resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Проверить статус подписки HomeEase")
    parser.add_argument("email", help="Email пользователя")
    parser.add_argument("password", help="Пароль")
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help=f"Базовый URL API (по умолчанию: {DEFAULT_API_URL})",
    )
    parser.add_argument("--json", action="store_true", help="Вывести сырой JSON")
    args = parser.parse_args()

    with httpx.Client(base_url=args.api_url.rstrip("/"), timeout=30.0) as client:
        token = login(client, args.email, args.password)
        status = fetch_status(client, token)

    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return

    print(f"API: {args.api_url}")
    print(f"Email: {args.email}")
    print("-" * 40)
    print(f"Статус:           {status.get('status')}")
    print(f"План:             {status.get('plan')}")
    print(f"Доступ:           {'да' if status.get('has_access') else 'нет'}")
    print(f"Осталось дней:    {status.get('days_remaining')}")
    print(f"Страна:           {status.get('country_code')}")
    print(f"Trial использован: {status.get('trial_used')}")
    if status.get("trial_end"):
        print(f"Конец trial:      {status.get('trial_end')}")
    if status.get("end_date"):
        print(f"Конец периода:    {status.get('end_date')}")
    pricing = status.get("pricing") or {}
    if pricing:
        print("-" * 40)
        print(f"Цена (месяц):     {pricing.get('monthly')}")
        print(f"Цена (год):       {pricing.get('yearly')}")
        print(f"Валюта:           {pricing.get('currency')}")


if __name__ == "__main__":
    main()
