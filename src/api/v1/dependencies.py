from uuid import UUID

from fastapi import Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.user import user_crud
from src.database.db_dependencies import get_async_session
from src.schemas.user import TelegramIDSchema


async def get_user_id(
    telegram_schema: TelegramIDSchema = Body(
        ...
    ),  # для отображения в сваггере
    session: AsyncSession = Depends(get_async_session),
) -> UUID:
    user_id = await user_crud.get_user_id_by_telegram_id(
        telegram_schema, session
    )
    if not user_id:
        raise HTTPException(
            status_code=404,
            detail='Пользователь с таким telegram_id не найден',
        )
    return user_id
