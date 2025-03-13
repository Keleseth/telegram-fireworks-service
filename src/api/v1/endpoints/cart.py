from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_dependencies import get_async_session

router = APIRouter()


@router.post(
    '/user/cart',
    status_code=status.HTTP_201_CREATED,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def add_product_to_cart(
    create_data: BaseModel,  # Создать свою схему.
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Добавить продукт в корзину.

    Доступен age_verified пользователям.
    """
    # TODO: Нужно в схему для энпоинта добавить поле telegram_id,
    # чтобы эндпоинт в теле запроса знал о пользователе.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Запрос выполнен успешно!'}


@router.get(
    '/user/cart',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def get_user_cart(
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Получить содержимое корзины пользователя.

    Доступен age_verified пользователям.
    """
    # TODO: Пагинация.
    # TODO: Необходимо получить telegram_id из тела запроса.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Запрос выполнен успешно!'}


@router.delete(
    '/user/cart/{firework_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def delete_product_from_cart(
    firework_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Удалить продукт из корзины пользователя.

    Доступен age_verified пользователям.
    """
    # TODO: Необходимо получить telegram_id из тела запроса.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Запрос выполнен успешно!'}
