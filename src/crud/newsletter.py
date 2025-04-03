import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.database.db_dependencies import get_async_session
from src.models.favorite import FavoriteFirework
from src.models.newsletter import AccountAge, Newsletter
from src.models.order import Order, OrderFirework
from src.models.product import Firework, FireworkTag
from src.models.user import User
from src.schemas.newsletter import NewsletterCreate, NewsletterUpdate

current_now = datetime.now(timezone.utc)


account_age_filters = {
    AccountAge.LESS_3_MONTHS: lambda: User.created_at
    >= current_now - timedelta(days=90),
    AccountAge.FROM_3_TO_12_MONTHS: lambda: and_(
        User.created_at < current_now - timedelta(days=90),
        User.created_at >= current_now - timedelta(days=365),
    ),
    AccountAge.FROM_1_TO_3_YEARS: lambda: and_(
        User.created_at < current_now - timedelta(days=365),
        User.created_at >= current_now - timedelta(days=365 * 3),
    ),
    AccountAge.MORE_THAN_3_YEARS: lambda: User.created_at
    < current_now - timedelta(days=365 * 3),
}


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
        """Фильтрует пользователей для рассылки на основе критериев."""
        order_count_subquery = (
            select(func.count(Order.id).label('order_count'))
            .where(Order.user_id == User.id)
            .scalar_subquery()
        )

        query = select(User)

        if newsletter.age_verified:
            query = query.where(User.age_verified.is_(True))

        if newsletter.account_age:
            query = query.where(account_age_filters[newsletter.account_age]())

        query = query.where(
            order_count_subquery >= newsletter.number_of_orders
        )

        if newsletter.users_related_to_tag and newsletter.tags:
            tag_ids = [tag.id for tag in newsletter.tags]

            # Проверка заказов с фейерверками нужных тегов
            order_subq = (
                select(1)
                .select_from(OrderFirework)
                .join(Firework, OrderFirework.firework_id == Firework.id)
                .join(FireworkTag, Firework.id == FireworkTag.firework_id)
                .where(
                    OrderFirework.order_id.in_(
                        select(Order.id).where(Order.user_id == User.id)
                    ),
                    FireworkTag.tag_id.in_(tag_ids),
                )
                .exists()
            )

            # Проверка избранного с нужными фейерверками
            favorite_subq = (
                select(1)
                .select_from(FavoriteFirework)
                .join(Firework, FavoriteFirework.firework_id == Firework.id)
                .join(FireworkTag, Firework.id == FireworkTag.firework_id)
                .where(
                    FavoriteFirework.user_id == User.id,
                    FireworkTag.tag_id.in_(tag_ids),
                )
                .exists()
            )

            query = query.where(or_(order_subq, favorite_subq))

        result = await session.execute(query)
        return result.scalars().all()

    # async def filtered_users_for_newsletter(
    #     self,
    #     newsletter: Newsletter,
    #     session: AsyncSession,
    # ) -> List[User]:
    #     """Фильтрует пользователей для рассылки на основе критериев.

    #     Аргументы:
    #         1. newsletter (Newsletter): объект рассылки.
    #         2. session (AsyncSession): объект сессии.

    #     Возвращаемое значение:
    #         List[User]: список пользователей, подходящих под критерии.
    #     """
    #     order_count_subquery = (
    #         select(func.count(Order.id).label('order_count'))
    #         .where(Order.user_id == User.id)
    #         .scalar_subquery()
    #     )
    #     query = select(User)
    #     if newsletter.age_verified:
    #         query = query.where(User.age_verified.is_(True))
    #     if newsletter.account_age:
    #         query = query.where(
    # account_age_filters[newsletter.account_age]())
    #     query = query.where(
    #         order_count_subquery >= newsletter.number_of_orders
    #     )
    #     result = await session.execute(query)
    #     return result.scalars().all()


newsletter_crud = NewsletterCRUD(Newsletter)


async def test_filter():
    session = await anext(get_async_session())
    newsletter = Newsletter(
        age_verified=True,
        account_age=AccountAge.MORE_THAN_3_YEARS,
        number_of_orders=1,
    )

    users = await newsletter_crud.filtered_users_for_newsletter(
        newsletter=newsletter, session=session
    )

    print(f'Найдено пользователей: {len(users)}')
    for user in users:
        print(user.id, user.created_at, user.age_verified)


if __name__ == '__main__':
    asyncio.run(test_filter())
