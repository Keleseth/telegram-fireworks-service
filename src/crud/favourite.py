from typing import Type, TypeVar
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.base import BaseJFModel
from src.models.favorite import FavoriteFirework
from src.schemas.favourite import FavoriteCreate
from src.models.product import Firework

ModelType = TypeVar('ModelType', bound=BaseJFModel)


class CRUDFavourite:
    """СRUD-класс для работы с избранными фейерверками."""

    def __init__(self, model: Type[ModelType]) -> None:
        """Инициализирует CRUD-класс с указанной моделью.

        Аргументы:
            model: SQLAlchemy-модель, связанная с таблицей в БД.
        """
        self.model = model

    async def create_favourite_by_telegram_id(
        self,
        obj_in: FavoriteCreate,
        user_id: UUID,
        session: AsyncSession,
    ):
        """Метод для добавления фейерверка в избранное по telegram_id."""
        obj_in_data = obj_in.dict()
        existing = await session.execute(
            select(self.model).where(
                self.model.user_id == user_id,
                self.model.firework_id == obj_in_data['firework_id']
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail="Этот фейерверк уже добавлен в избранное"
            )
        firework = await session.execute(
            select(Firework).where(
                id == obj_in_data['firework_id']
            )
        )
        if not firework.scalar_one_or_none():
            raise HTTPException(
                status_code=404,
                detail="Такого фейерверка не существует"
            )
        db_obj = self.model(
            user_id=user_id,
            firework_id=obj_in_data['firework_id']
        )
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_multi_by_telegram_id(
        self,
        user_id: UUID,
        session: AsyncSession,
    ):
        """Метод для получения избранных по telegram_id."""
        query = (
            select(self.model)
            .options(joinedload(self.model.firework))
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at)
        )
        db_objs = await session.execute(query)
        return db_objs.unique().scalars().all()

    async def remove_by_telegram_id(
        self,
        user_id: UUID,
        firework_id: int,
        session: AsyncSession,
    ):
        """Метод для удаления избранных по telegram_id."""
        db_obj = await session.scalar(
            select(self.model)
            .options(selectinload(self.model.firework))
            .where(
                self.model.user_id == user_id,
                self.model.firework_id == firework_id,
            )
        )
        if db_obj is None:
            raise HTTPException(
                status_code=404, detail='Избранное не найдено.'
            )
        firework_name = db_obj.firework.name
        await session.delete(db_obj)
        await session.commit()
        return firework_name


favorite_crud = CRUDFavourite(FavoriteFirework)
