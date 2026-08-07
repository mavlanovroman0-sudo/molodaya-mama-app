"""AI эндпоинты-заглушки / AI stub endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.models import User
from app.services.ai import predict_price, substitute_ingredient
from app.services.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["ai"])


class PriceRequest(BaseModel):
    product: str


class IngredientRequest(BaseModel):
    description: str


@router.post("/price-prediction")
async def price_prediction(body: PriceRequest, user: User = Depends(get_current_user)):
    """ИИ-скаут «Где дешевле»."""
    return await predict_price(body.product, user.district or "", user.language.value)


@router.post("/ingredient-substitute")
async def ingredient_substitute(body: IngredientRequest, user: User = Depends(get_current_user)):
    """«Вкус мира» — замена ингредиентов."""
    return await substitute_ingredient(body.description, user.district or user.city or "RU", user.language.value)
