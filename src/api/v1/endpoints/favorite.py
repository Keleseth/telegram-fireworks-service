from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.favourite import favorite_crud
from src.database.db_dependencies import get_async_session
from src.schemas.favourite import FavoriteCreate, FavoriteDB, FavoriteMulti

router = APIRouter()


@router.post(
    '/favorites',
    status_code=status.HTTP_201_CREATED,
    response_model=FavoriteDB,
)
async def add_favorite_firework(
    create_data: FavoriteCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Добавить фейерверк в избранное."""
    return await favorite_crud.create_favourite_by_telegram_id(
        create_data, session
    )


@router.post(
    '/favorites/me',
    status_code=status.HTTP_200_OK,
    response_model=list[FavoriteDB],
)
async def get_favorite_fireworks(
    telegram_data: FavoriteMulti,
    session: AsyncSession = Depends(get_async_session),
):
    """Получить список избранных фейерверков пользователя."""
    return await favorite_crud.get_multi_by_telegram_id(telegram_data, session)


@router.delete(
    '/favorites/{firework_id}',
    status_code=status.HTTP_200_OK,
    response_model=FavoriteDB,
)
async def remove_favorite_firework(
    firework_id: int,
    telegram_data: FavoriteMulti,
    session: AsyncSession = Depends(get_async_session),
):
    """Удалить фейерверк из избранного."""
    return await favorite_crud.remove_by_telegram_id(
        telegram_data, firework_id, session
    )
