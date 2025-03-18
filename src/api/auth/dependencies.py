from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.dependencies import get_async_session
from src.crud.user import user_crud
from src.models.user import User


async def current_user(
    telegram_id: int, session: AsyncSession = Depends(get_async_session)
) -> User:
    """Проверяет текущего пользовтаеля на существование и is_active=True."""
    user = await user_crud.get_user_by_telegram_id(session, telegram_id)
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
    """Доступ только для совершеннолетних."""
    if not user.age_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ только для совершеннолетних.',
        )
    return user


async def current_admin(user: User = Depends(current_user)) -> User:
    """Доступ только для адина и суперюзера."""
    if not (user.is_admin or user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ только для администраторов.',
        )
    return user
