from fastapi import Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.auth import user_admin_token
from src.crud.user import user_crud
from src.database.db_dependencies import get_async_session
from src.models.user import User
from src.schemas.user import TelegramIDSchema


async def current_user(
    telegram_schema: TelegramIDSchema = Body(...),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Проверяет текущего пользователя на существование и is_active=True.

    Параметры функции:
    1) telegram_id - id пользователя telegram;
    2) session - асинхронный сессия для работы с БД.
    """
    user = await user_crud.get_user_by_telegram_id(
        telegram_schema.telegram_id, session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден.',
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Аккаунт деактивирован.',
        )
    return user


async def current_age_verified_user(
    user: User = Depends(current_user),
) -> User:
    """Доступ только для совершеннолетних.

    Параметры функции:
    1) user - объект пользователя модели User.
    """
    if not user.age_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ только для совершеннолетних.',
        )
    return user


async def current_admin(
    telegram_schema: TelegramIDSchema = Body(...),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Доступ только для адина и суперюзера.

    Получате админа по telegram_id.

    Параметры функции:
    1) telegram_schema - pydantic cхема c telegram_id пользователя;
    2) user - объект пользователя модели User.
    """
    user = await user_crud.get_user_by_telegram_id(
        telegram_schema.telegram_id, session
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден!',
        )
    if not (user.is_admin or user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ только для администраторов.',
        )
    return user


async def current_admin_with_token(
    user: User = Depends(user_admin_token),
) -> User:
    """Доступ только для админа и суперюзера, с действующим токеном.

    Параметры функции:
    1) user - объект пользователя модели User.
    """
    if not (user.is_admin or user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ только для администраторов.',
        )
    return user
