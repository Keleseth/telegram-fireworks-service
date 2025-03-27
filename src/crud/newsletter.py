from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models import Newsletter, Order, User
from src.schemas.newsletter import NewsletterCreate, NewsletterUpdate


class NewsletterCRUD(CRUDBase[Newsletter, NewsletterCreate, NewsletterUpdate]):
    """Класс для CRUD операций модели Newsletter."""

    async def get_all_unsett_newslatter(
        self,
        session: AsyncSession,
    ) -> Optional[list[Newsletter]]:
        """Возвращает все объекты рассылок Newsletter, которые не отправлены.

        Параметры:
            1. session (AsyncSession): объект сессии.

        Возвращаемое значение:
            list[Newsletter]: список всех объектов модели Newsletter.
        """
        all_newslatters = await session.execute(
            select(Newsletter).where(Newsletter.switch_send.is_(False))
        )
        return all_newslatters.scalars().all()

    async def filtered_users_for_newsletter(
        self,
        newsletter: Newsletter,
        session: AsyncSession,
    ) -> List[User]:
        """Фильтрует пользователей для рассылки на основе критериев.

        Аргументы:
            1. newsletter (Newsletter): объект рассылки.
            2. session (AsyncSession): объект сессии.

        Возвращаемое значение:
            List[User]: список пользователей, подходящих под критерии.
        """
        order_count_subquery = (
            select(func.count(Order.id).label('order_count'))
            .where(Order.user_id == User.id)
            .scalar_subquery()
        )
        query = select(User)
        if newsletter.age_verified:
            query = query.where(User.age_verified.is_(True))
        # result = await session.execute(query)
        # users = result.scalars().all()
        # filtered_users = []
        # for user in users:
        #     order_count = len(user.orders)
        #     if order_count >= newsletter.number_of_orders:
        #         filtered_users.append(user)
        query = query.where(
            order_count_subquery >= newsletter.number_of_orders
        )
        result = await session.execute(query)
        return result.scalars().all()


newsletter_crud = NewsletterCRUD(Newsletter)
