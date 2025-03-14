from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_dependencies import get_async_session

router = APIRouter()


@router.post(
    '/favorites',
    status_code=status.HTTP_201_CREATED,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def add_favorite_firework(
    create_data: BaseModel,  # Добавить схему с telegram_id и firework_id
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Добавить фейерверк в избранное."""
    # TODO: Нужно в схему для энпоинта добавить поле telegram_id,
    # чтобы эндпоинт в теле запроса знал о пользователе.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Фейерверк добавлен в избранное'}


@router.get(
    '/favorites/me',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def get_favorite_fireworks(
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Получить список избранных фейерверков пользователя."""
    # TODO: Необходимо получить telegram_id из тела запроса.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Список избранных фейерверков получен'}


@router.delete(
    '/favorites/{firework_id}',
    status_code=status.status.HTTP_200_OK,
    response_model=dict[str, str],  # заменить на кастомную схему
)
async def remove_favorite_firework(
    firework_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """Удалить фейерверк из избранного."""
    # TODO: Необходимо получить telegram_id из тела запроса.
    # НЕ добавлять telegram_id в path или query параметры.
    return {'message': 'Фейерверк удален из избранного'}
