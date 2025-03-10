from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_dependencies import get_async_session

router = APIRouter()


@router.post(
    '/user/address',
    status_code=status.HTTP_201_CREATED,
    response_model=dict[str, str],
)
async def create_user_address(
    create_data: BaseModel,  # Создать свою схему.
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Добавить продукт в корзину Доступен age_verified пользователям."""
    # TODO: Нужно в схему для энпоинта добавить поле telegram_id,
    # чтобы эндпоинт в теле запроса знал о пользователе.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Запрос выполнен успешно!'}


@router.get(
    '/user/address',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, str],
)
async def get_user_address(
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Добавить продукт в корзину Доступен age_verified пользователям."""
    # TODO: Необходимо получить telegram_id из тела запроса.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Запрос выполнен успешно!'}


@router.patch(
    '/user/address',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, str],
)
async def update_user_address(
    data_update: BaseModel,  # Создать свою схему.
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Добавить продукт в корзину Доступен age_verified пользователям."""
    # TODO: Нужно в схему для энпоинта добавить поле telegram_id,
    # чтобы эндпоинт в теле запроса знал о пользователе.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Запрос выполнен успешно!'}


@router.delete(
    '/user/address',
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=dict[str, str],
)
async def delete_user_address(
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Добавить продукт в корзину Доступен age_verified пользователям."""
    # TODO: Необходимо получить telegram_id из тела запроса.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Запрос выполнен успешно!'}
