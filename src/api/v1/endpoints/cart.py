from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.cart import cart_crud
from src.database.db_dependencies import get_async_session
from src.schemas.cart import (
    CreateCartSchema,
    DeleteCartSchema,
    MessageResponse,
    ReadCartSchema,
)

router = APIRouter()


@router.post(
    '/user/cart',
    status_code=status.HTTP_201_CREATED,
    response_model=MessageResponse,
)
async def add_product_to_cart(
    create_data: CreateCartSchema,
    session: AsyncSession = Depends(get_async_session),
) -> MessageResponse:
    """Добавить продукт в корзину.

    Доступен age_verified пользователям.
    """
    await cart_crud.add_to_cart(create_data.telegram_id, create_data, session)
    return MessageResponse(message='Товар успешно добален в корзину!')


@router.get(
    '/user/cart',
    status_code=status.HTTP_200_OK,
    response_model=List[ReadCartSchema],
)
async def get_user_cart(
    telegram_data: CreateCartSchema,
    limit: int = 10,
    offset: int = 0,
    session: AsyncSession = Depends(get_async_session),
) -> List[ReadCartSchema]:
    """Получить содержимое корзины пользователя.

    Доступен age_verified пользователям.
    """
    cart_items = await cart_crud.get_by_user(
        telegram_data.telegram_id, session
    )
    return cart_items[offset : offset + limit]


@router.delete(
    '/user/cart/{firework_id}',
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
)
async def delete_product_from_cart(
    delete_data: DeleteCartSchema,
    session: AsyncSession = Depends(get_async_session),
) -> MessageResponse:
    """Удалить продукт из корзины пользователя.

    Доступен age_verified пользователям.
    """
    cart_item = await cart_crud.get_cart_item(
        delete_data.telegram_id, delete_data.firework_id, session
    )
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Товар не найден в корзине',
        )
    await cart_crud.remove(cart_item, session)
    return MessageResponse(message='Товар удалён из корзины!')
