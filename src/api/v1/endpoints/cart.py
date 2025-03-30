from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.cart import cart_crud
from src.database.db_dependencies import (
    get_async_session,
    get_user_id,
    pagination_params,
)
from src.schemas.cart import (
    CreateCartSchema,
    MessageResponse,
    ReadCartSchema,
    UpdateCartSchema,
)

router = APIRouter()


@router.post(
    '/user/cart',
    status_code=status.HTTP_201_CREATED,
    response_model=MessageResponse,
)
async def add_product_to_cart(
    create_data: CreateCartSchema,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_async_session),
) -> MessageResponse:
    """Добавить продукт в корзину.

    Доступен age_verified пользователям.
    """
    await cart_crud.add_to_cart(user_id, create_data, session)
    return MessageResponse(message='Товар успешно добавлен в корзину!')


@router.post(
    '/user/cart/me',
    status_code=status.HTTP_200_OK,
    response_model=List[ReadCartSchema],
)
async def get_user_cart(
    user_id: UUID = Depends(get_user_id),
    pagination: tuple[int, int] = Depends(pagination_params),
    session: AsyncSession = Depends(get_async_session),
) -> List[ReadCartSchema]:
    """Получить содержимое корзины пользователя.

    Доступен age_verified пользователям.
    """
    limit, offset = pagination
    cart_items = await cart_crud.get_by_user(user_id, session)
    return cart_items[offset : offset + limit]


@router.patch(
    '/user/cart/{firework_id}',
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
)
async def update_product_amount(
    firework_id: int,
    update_data: UpdateCartSchema,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_async_session),
) -> MessageResponse:
    """Устанавливает новое количество товара в корзине."""
    update_item = await cart_crud.update_cart_item(
        user_id, firework_id, update_data, session
    )
    if update_item is None:
        return MessageResponse(message='Товар не найден или не обновлен')
    return MessageResponse(message='Товар успешно обновлен')


@router.delete(
    '/user/cart/{firework_id}',
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
)
async def delete_product_from_cart(
    firework_id: int,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_async_session),
) -> MessageResponse:
    """Удалить продукт из корзины пользователя.

    Доступен age_verified пользователям.
    """
    try:
        await cart_crud.remove(user_id, firework_id, session)
        return MessageResponse(message='Товар успешно удален из корзины.')
    except Exception as e:
        return MessageResponse(message=f'Ошибка при удалении товара: {str(e)}')


@router.delete(
    '/user/cart/',
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
)
async def clear_user_cart(
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_async_session),
) -> MessageResponse:
    """Очистить корзину пользователя полностью.

    Доступен age_verified пользователям.
    """
    await cart_crud.clear_cart(user_id, session)
    return MessageResponse(message='Корзина успешно очищена!')
