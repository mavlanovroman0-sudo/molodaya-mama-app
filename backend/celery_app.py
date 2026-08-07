"""Celery application / Celery app for scheduled tasks."""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "homeease",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "invite-reminder-daily": {
            "task": "app.tasks.celery_send_invite_reminder",
            "schedule": crontab(hour=10, minute=0),
        },
    },
)


@celery_app.task(name="app.tasks.celery_send_invite_reminder")
def celery_send_invite_reminder():
    from app.tasks import send_invite_reminder_sync

    return send_invite_reminder_sync()
