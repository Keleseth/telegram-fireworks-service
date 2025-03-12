from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from src.crud.base import CRUDBase
from src.models.order import Order, OrderFirework, OrderStatus
from src.models.user import User
from src.schemas.order import (
    CreateOrderSchema,
    DeleteOrderSchema,
    OrderFireworkSchema,
    ReadOrderSchema,
    UpdateOrderSchema,
)


class CRUDOrder(CRUDBase[Order, CreateOrderSchema, UpdateOrderSchema]):
    """CRUD операции с заказами."""

    async def get_user_id_by_telegram_id(
        self, db: AsyncSession, telegram_id: int
    ) -> UUID:
        """Получить UUID пользователя по telegram_id."""
        query = select(User).filter(User.telegram_id == telegram_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=404,
                detail='Пользователь с таким telegram_id не найден',
            )
        return user.id

    async def create_order(
        self, db: AsyncSession, order_data: CreateOrderSchema
    ) -> ReadOrderSchema:
        """Создать новый заказ."""
        user_id = await self.get_user_id_by_telegram_id(
            db, order_data.telegram_id
        )
        new_order = Order(
            user_id=user_id,
            status_id=1,  # ID статуса 'Создан'
            user_address_id=order_data.user_address_id,
        )
        db.add(new_order)
        await db.flush()
        order_fireworks = [
            OrderFirework(order_id=new_order.id, **item.dict())
            for item in order_data.order_fireworks
        ]
        db.add_all(order_fireworks)
        await db.commit()
        await db.refresh(new_order, attribute_names=['order_fireworks'])
        status_text = (
            (
                await db.execute(
                    select(OrderStatus).filter(
                        OrderStatus.id == new_order.status_id
                    )
                )
            )
            .scalar_one()
            .status_text
        )
        return ReadOrderSchema(
            id=new_order.id,
            status=status_text,
            user_address_id=new_order.user_address_id,
            order_fireworks=[
                OrderFireworkSchema.from_orm(fw)
                for fw in new_order.order_fireworks
            ],
            user_id=new_order.user_id,
        )

    async def get_orders_by_user(
        self, db: AsyncSession, telegram_id: int
    ) -> List[ReadOrderSchema]:
        """Получить все заказы пользователя."""
        user_id = await self.get_user_id_by_telegram_id(db, telegram_id)
        query = (
            select(Order)
            .options(
                joinedload(Order.order_fireworks), joinedload(Order.status)
            )
            .filter(Order.user_id == user_id)
        )
        result = await db.execute(query)
        orders = result.unique().scalars().all()
        return [
            ReadOrderSchema(
                id=order.id,
                status=order.status.status_text,
                user_address_id=order.user_address_id,
                order_fireworks=[
                    OrderFireworkSchema.from_orm(fw)
                    for fw in order.order_fireworks
                ],
                user_id=order.user_id,
            )
            for order in orders
        ]

    async def update_order(
        self, db: AsyncSession, order_data: UpdateOrderSchema, order_id: int
    ) -> ReadOrderSchema:
        """Обновить заказ, если он ещё не обработан."""
        user_id = await self.get_user_id_by_telegram_id(
            db, order_data.telegram_id
        )
        query = select(Order).filter(
            Order.id == order_id, Order.user_id == user_id
        )
        result = await db.execute(query)
        order = result.scalar_one_or_none()
        if not order or order.status_id != 1:
            return None
        if order_data.user_address_id is not None:
            order.user_address_id = order_data.user_address_id
        if order_data.order_fireworks is not None:
            await db.execute(
                select(OrderFirework)
                .filter(OrderFirework.order_id == order_id)
                .delete()
            )
            new_items = [
                OrderFirework(order_id=order_id, **item.dict())
                for item in order_data.order_fireworks
            ]
            db.add_all(new_items)
        await db.commit()
        await db.refresh(order, attribute_names=['order_fireworks'])
        status_text = (
            (
                await db.execute(
                    select(OrderStatus).filter(
                        OrderStatus.id == order.status_id
                    )
                )
            )
            .scalar_one()
            .status_text
        )
        return ReadOrderSchema(
            id=order.id,
            status=status_text,
            user_address_id=order.user_address_id,
            order_fireworks=[
                OrderFireworkSchema.from_orm(fw)
                for fw in order.order_fireworks
            ],
            user_id=order.user_id,
        )

    async def delete_order(
        self, db: AsyncSession, order_data: DeleteOrderSchema
    ) -> bool:
        """Удалить заказ, если он ещё не обработан."""
        user_id = await self.get_user_id_by_telegram_id(
            db, order_data.telegram_id
        )
        query = select(Order).filter(
            Order.id == order_data.order_id, Order.user_id == user_id
        )
        result = await db.execute(query)
        order = result.scalar_one_or_none()
        if not order or order.status_id != 1:
            return False
        await db.delete(order)
        await db.commit()
        return True


crud_order = CRUDOrder(Order)
