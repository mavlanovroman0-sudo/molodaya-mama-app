#!/usr/bin/env python3
"""
Тест webhook YooKassa: отправка mock payment.succeeded и проверка статуса подписки.

  python -m scripts.test_webhook --email test@homeease.com --password Test1234
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import uuid

import httpx

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_API = os.environ.get("API_URL", "http://localhost:8001")


def login(client: httpx.Client, email: str, password: str) -> str:
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    r.raise_for_status()
    return r.json()["access_token"]


def get_user_id(client: httpx.Client, token: str) -> str:
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    return r.json()["id"]


def get_status(client: httpx.Client, token: str) -> dict:
    r = client.get(
        "/api/v1/user/subscription-status",
        headers={"Authorization": f"Bearer {token}"},
    )
    r.raise_for_status()
    return r.json()


def build_yookassa_succeeded_event(user_id: str, plan: str = "monthly") -> dict:
    payment_id = f"pay_test_{uuid.uuid4().hex[:12]}"
    return {
        "type": "notification",
        "event": "payment.succeeded",
        "object": {
            "id": payment_id,
            "status": "succeeded",
            "paid": True,
            "metadata": {
                "user_id": user_id,
                "plan": plan,
                "country_code": "RU",
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Тест YooKassa webhook HomeEase")
    parser.add_argument("--email", default="test@homeease.com")
    parser.add_argument("--password", default="Test1234")
    parser.add_argument("--api-url", default=DEFAULT_API)
    parser.add_argument("--plan", default="monthly", choices=("monthly", "yearly"))
    args = parser.parse_args()

    base = args.api_url.rstrip("/")
    with httpx.Client(base_url=base, timeout=30.0) as client:
        try:
            token = login(client, args.email, args.password)
            user_id = get_user_id(client, token)
            before = get_status(client, token)
            logger.info("До webhook: status=%s", before.get("status"))
        except httpx.HTTPError as e:
            logger.error("Auth failed: %s", e)
            return 1

        event = build_yookassa_succeeded_event(user_id, args.plan)
        resp = client.post(
            "/api/v1/webhook/yookassa",
            content=json.dumps(event).encode(),
            headers={"Content-Type": "application/json"},
        )
        logger.info("Webhook: %s %s", resp.status_code, resp.text[:200])

        if resp.status_code not in (200, 201):
            return 1

        after = get_status(client, token)
        logger.info("После webhook: status=%s plan=%s", after.get("status"), after.get("plan"))

        if after.get("status") == "active":
            print("✅ Подписка активирована через YooKassa webhook.")
            return 0

        print("⚠️  Статус не изменился. При реальном YooKassa включите верификацию через API.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
