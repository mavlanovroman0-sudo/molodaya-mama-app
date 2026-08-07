"""Начисление жетонов / Token balance service."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TokenTransaction, User


async def add_jetons(
    db: AsyncSession,
    user: User,
    amount: int,
    reason: str,
) -> int:
    """Начисляет жетоны и пишет в историю. Возвращает новый баланс."""
    user.add_jetons(amount)
    db.add(TokenTransaction(user_id=user.id, amount=amount, reason=reason))
    await db.flush()
    return user.token_balance
