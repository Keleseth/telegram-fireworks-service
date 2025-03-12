from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_dependencies import get_async_session

router = APIRouter()


@router.post(
    '/orders',
    status_code=status.HTTP_201_CREATED,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def create_user_order(
    create_data: BaseModel,  # Создать cхему для эндпоинта
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Создать заказ для пользователя."""
    # TODO: Нужно в схему для энпоинта добавить поле telegram_id,
    # чтобы эндпоинт в теле запроса знал о пользователе.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Запрос выполнен успешно!'}


@router.get(
    '/orders/me',
    status_code=status.HTTP_201_CREATED,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def get_user_orders(
    create_data: BaseModel,  # Создать cхему для эндпоинта
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Получить все заказы пользователя."""
    # TODO: Выяснить, как нужно получать историю заказов, отдельно открытые,
    # отдельно закрытые?
    # TODO: Необходимо получить telegram_id из тела запроса.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Запрос выполнен успешно!'}


@router.get(
    '/orders/{order_id}',
    status_code=status.HTTP_201_CREATED,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def get_user_order(
    order_id: int,
    create_data: BaseModel,  # Создать cхему для эндпоинта
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Получить конкретный заказ пользователя."""
    # TODO: Необходимо получить telegram_id из тела запроса.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Запрос выполнен успешно!'}


@router.patch(
    '/orders/{order_id}',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def update_user_order(
    order_id: int,
    create_data: BaseModel,  # Создать cхему для эндпоинта
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Изменить доступные для изменения поля заказа.

    Доступные поля:
        Адрес доставки заказа.
        Статус заказа(в том числе для отмены).
    """
    # TODO: Нужно в схему для энпоинта добавить поле telegram_id,
    # чтобы эндпоинт в теле запроса знал о пользователе.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Запрос выполнен успешно!'}

