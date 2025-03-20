from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.favourite import favorite_crud
from src.crud.user import user_crud
from src.database.db_dependencies import get_async_session
from src.schemas.favourite import (
    FavoriteCreate,
    FavoriteDBCreate,
    FavoriteDBGet,
)
from src.schemas.user import TelegramIDSchema

router = APIRouter()


@router.post(
    '/favorites',
    status_code=status.HTTP_201_CREATED,
    response_model=FavoriteDBCreate,
)
async def add_favorite_firework(
    create_data: FavoriteCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Добавить фейерверк в избранное."""
    user_id = await user_crud.get_user_id_by_telegram_id(
        create_data, session=session
    )
    print(user_id)
    return await favorite_crud.create_favourite_by_telegram_id(
        create_data, user_id, session
    )


@router.post(
    '/favorites/me',
    status_code=status.HTTP_200_OK,
    response_model=list[FavoriteDBGet],
)
async def get_favorite_fireworks(
    telegram_id_data: TelegramIDSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Получить список избранных фейерверков пользователя."""
    user_id = await user_crud.get_user_id_by_telegram_id(
        telegram_id_data, session=session
    )
    return await favorite_crud.get_multi_by_telegram_id(user_id, session)


@router.delete(
    '/favorites/{firework_id}',
    status_code=status.HTTP_200_OK,
)
async def remove_favorite_firework(
    firework_id: int,
    telegram_id_data: TelegramIDSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Удалить фейерверк из избранного."""
    user_id = await user_crud.get_user_id_by_telegram_id(
        telegram_id_data, session=session
    )
    deleted_firework_name = await favorite_crud.remove_by_telegram_id(
        user_id, firework_id, session
    )
    return {
        'message': f'Фейерверк: {deleted_firework_name} удален из избранного.'
    }
