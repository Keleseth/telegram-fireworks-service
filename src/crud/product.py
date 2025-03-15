from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.product import Category, Firework


class FireworkCRUD(CRUDBase):
    async def get_by_category(
        self, category_id: int, session: AsyncSession
    ) -> list[Firework]:
        return await session.execute(
            select(Firework).where(Firework.category.id == category_id)
        )


firework_crud = FireworkCRUD(Firework)
category_crud = CRUDBase(Category)
