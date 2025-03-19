from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase, ModelType
from src.models.discounts import Discount
from src.models.product import Firework


class CRUDDiscounts(CRUDBase):
    """CRUD-класс для работы с объектами Discount."""

    async def get_all_discounts(
        self, session: AsyncSession
    ) -> Optional[ModelType]:
        """Получает все акции.

        Аргументы:
            1. session (AsyncSession): объект сессии.

        Возвращаемое значение:
            Акции.
        """
        result = await session.execute(
            select(Discount).options(selectinload(Discount.fireworks))
        )
        return result.scalars().all()

    async def get_fireworks_by_discount_id(
        self, session: AsyncSession, discount_id: int
    ):
        """Получает все фейрверки по айди акции.

        Аргументы:
            1. session (AsyncSession): объект сессии.
            2. discount_id (int): айди акции.

        Возвращаемое значение:
            Фейерверки.
        """
        result = await session.execute(
            select(Firework).where(Discount.id == discount_id)
        )
        return result.scalars().all()


discounts_crud = CRUDDiscounts(Discount)
