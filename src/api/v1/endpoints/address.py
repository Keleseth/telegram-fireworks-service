from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_dependencies import get_async_session

router = APIRouter()


@router.post(
    '/addresses',
    status_code=status.HTTP_201_CREATED,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def create_user_address(
    create_data: BaseModel,  # Создать свою схему.
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Создать адрес пользователя."""
    # TODO: Нужно в схему для энпоинта добавить поле telegram_id,
    # чтобы эндпоинт в теле запроса знал о пользователе.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Запрос выполнен успешно!'}


@router.get(
    '/addresses',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def get_user_addressess(
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Получить адреса пользователя."""
    # TODO: Необходимо получить telegram_id из тела запроса.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Запрос выполнен успешно!'}


@router.get(
    '/addresses/{address_id}',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def get_user_address(
    address_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Получить конкретный адрес пользователя по id."""
    return {'message': 'Запрос выполнен успешно!'}


@router.patch(
    '/addresses/{address_id}',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def update_user_address(
    address_id: str,
    data_update: BaseModel,  # Создать свою схему.
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Изменить адрес пользователя."""
    # TODO: Нужно в схему для энпоинта добавить поле telegram_id,
    # чтобы эндпоинт в теле запроса знал о пользователе.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Запрос выполнен успешно!'}


@router.delete(
    '/address/{address_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def delete_user_address(
    address_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Удалить адрес пользователя."""
    # TODO: Необходимо получить telegram_id из тела запроса.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Запрос выполнен успешно!'}
