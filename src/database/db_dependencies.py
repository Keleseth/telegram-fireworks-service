from typing import Any, AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.crud.user import user_crud
from src.schemas.cart import UserIdentificationSchema

engine = create_async_engine(settings.database_url)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, Any]:
    async with AsyncSessionLocal() as async_session:
        yield async_session


async def get_user_id(
    user_ident: UserIdentificationSchema,
    session: AsyncSession = Depends(get_async_session),
) -> UUID:
    user_id: UUID | None = await user_crud.get_user_id_by_telegram_id(
        user_ident, session
    )
    if not user_id:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    return user_id


def pagination_params(
    limit: int = Query(10, ge=1, le=100, description='Максимум 100'),
    offset: int = Query(0, ge=0, description='Пропустить N записей'),
) -> tuple[int, int]:
    """Параметры пагинации для списков."""
    return limit, offset
