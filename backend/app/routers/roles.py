"""Переключение роли и дашборд / Role switch & dashboard."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import DashboardResponse, RoleSwitchRequest
from app.services.auth import get_current_user
from app.services.dashboard import get_dashboard

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/switch", response_model=DashboardResponse)
async def switch_role(
    body: RoleSwitchRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Переключение между «Домохозяйка» и «Молодая мама»."""
    user.active_role = body.role
    await db.flush()
    return get_dashboard(user.active_role, user.token_balance, user.district)


@router.get("/dashboard", response_model=DashboardResponse)
async def current_dashboard(user: User = Depends(get_current_user)):
    """Текущий ролевой дашборд с полным списком функций."""
    return get_dashboard(user.active_role, user.token_balance, user.district)
