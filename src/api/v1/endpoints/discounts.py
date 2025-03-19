from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.discounts import discounts_crud
from src.database.db_dependencies import get_async_session
from src.schemas.discounts import (
    ReadDiscountsSchema,
    TelegramIdDiscountsSchema,
)
from src.schemas.product import FireworkBase

router = APIRouter()


@router.post(
    '/discounts',
    status_code=status.HTTP_200_OK,
    response_model=List[ReadDiscountsSchema],
)
async def get_disctounts(
    schema: TelegramIdDiscountsSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение всех акций."""
    return await discounts_crud.get_all_discounts(session)


@router.post(
    '/discounts/{discount_id}',
    status_code=status.HTTP_200_OK,
    response_model=List[FireworkBase],
)
async def get_user_address(
    discount_id: str,
    schema: TelegramIdDiscountsSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Получить все фейерверки связанные с конкретной акцией по её id."""
    return await discounts_crud.get_fireworks_by_discount_id(
        session, int(discount_id)
    )
