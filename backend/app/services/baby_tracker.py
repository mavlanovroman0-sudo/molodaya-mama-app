"""Трекер мамы: кормление, сон, подгузник + прогнозы / Baby tracker service."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Baby, DiaperLog, FeedingLog, SleepLog, User
from app.schemas import (
    BabyTrackerSummary,
    FeedingPrediction,
    SleepPhasePrediction,
)
from app.schemas import BabyResponse as BabySchema
from app.services.ai import predict_feeding_peaks, predict_sleep_phase


async def get_baby_or_404(db: AsyncSession, baby_id: UUID, user: User) -> Baby:
    result = await db.execute(select(Baby).where(Baby.id == baby_id, Baby.user_id == user.id))
    baby = result.scalar_one_or_none()
    if not baby:
        raise ValueError("baby_not_found")
    return baby


def _age_months(birth_date) -> int:
    today = datetime.now(timezone.utc).date()
    return (today.year - birth_date.year) * 12 + (today.month - birth_date.month)


async def log_feeding(db: AsyncSession, baby: Baby, data: dict) -> FeedingLog:
    log = FeedingLog(baby_id=baby.id, **data)
    db.add(log)
    await db.flush()
    return log


async def log_sleep(db: AsyncSession, baby: Baby, data: dict) -> SleepLog:
    log = SleepLog(baby_id=baby.id, **data)
    db.add(log)
    await db.flush()
    return log


async def log_diaper(db: AsyncSession, baby: Baby, data: dict) -> DiaperLog:
    log = DiaperLog(baby_id=baby.id, **data)
    db.add(log)
    await db.flush()
    return log


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


async def get_tracker_summary(db: AsyncSession, baby: Baby, language: str = "ru") -> BabyTrackerSummary:
    feeding_result = await db.execute(
        select(FeedingLog).where(FeedingLog.baby_id == baby.id).order_by(FeedingLog.logged_at.desc()).limit(20)
    )
    sleep_result = await db.execute(
        select(SleepLog).where(SleepLog.baby_id == baby.id).order_by(SleepLog.sleep_start.desc()).limit(10)
    )
    diaper_result = await db.execute(
        select(DiaperLog).where(DiaperLog.baby_id == baby.id).order_by(DiaperLog.logged_at.desc()).limit(1)
    )

    feedings = feeding_result.scalars().all()
    sleeps = sleep_result.scalars().all()
    last_diaper = diaper_result.scalar_one_or_none()

    age = _age_months(baby.birth_date)
    feeding_logs = [{"type": f.feeding_type, "at": f.logged_at.isoformat()} for f in feedings]
    sleep_logs = [{"start": s.sleep_start.isoformat(), "end": s.sleep_end.isoformat() if s.sleep_end else None} for s in sleeps]

    fp = await predict_feeding_peaks(age, feeding_logs, language)
    sp = await predict_sleep_phase(age, sleep_logs, language)

    return BabyTrackerSummary(
        baby=BabySchema.model_validate(baby),
        last_feeding=feedings[0].logged_at if feedings else None,
        last_sleep=sleeps[0].sleep_start if sleeps else None,
        last_diaper=last_diaper.logged_at if last_diaper else None,
        feeding_prediction=FeedingPrediction(
            next_peak_at=_parse_iso_datetime(fp.get("next_peak_at")),
            evening_chaos_warning=fp.get("evening_chaos_warning", False),
            message_key="feeding.evening_warning" if fp.get("evening_chaos_warning") else "feeding.normal",
            interval_hours_avg=fp.get("interval_hours_avg"),
        ),
        sleep_prediction=SleepPhasePrediction(
            current_phase=sp.get("current_phase", "unknown"),
            confidence=sp.get("confidence", 0),
            next_wake_window=_parse_iso_datetime(sp.get("next_wake_window")),
        ),
    )
