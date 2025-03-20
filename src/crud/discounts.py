from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase, ModelType
from src.models.discounts import Discount
from src.models.product import Firework


class CRUDDiscounts(CRUDBase):
    """CRUD-класс для работы с объектами Discount."""

    async def get_all_discounts(
        self, session: AsyncSession
    ) -> Optional[ModelType]:
        """Получает все активные акции.

        Аргументы:
            1. session (AsyncSession): объект сессии.

        Возвращаемое значение:
            Активные акции.
        """
        moscow_time = datetime.utcnow()
        active_discounts = await session.execute(
            select(Discount).where(
                Discount.start_date <= moscow_time,
                Discount.end_date >= moscow_time,
            )
        )
        return active_discounts.scalars().all()

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
        fireworks = await session.execute(
            select(Firework).where(
                Firework.discounts.any(Discount.id == discount_id)
            )
        )
        return fireworks.unique().scalars().all()


discounts_crud = CRUDDiscounts(Discount)
