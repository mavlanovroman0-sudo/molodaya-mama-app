"""Remote Config (MVP — API вместо Firebase) / Remote configuration."""

from fastapi import APIRouter

router = APIRouter(prefix="/config", tags=["config"])

DEFAULT_CONFIG = {
    "show_invite_banner": True,
}


@router.get("/remote")
async def get_remote_config():
    """Параметры для фронтенда (аналог Firebase Remote Config)."""
    return DEFAULT_CONFIG
