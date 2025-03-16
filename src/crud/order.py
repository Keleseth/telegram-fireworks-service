from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.crud.base import CRUDBase
from src.models.cart import Cart
from src.models.order import Order, OrderFirework
from src.schemas.order import (
    CreateOrderSchema,
    OrderFireworkSchema,
    ReadOrderSchema,
    UpdateOrderAddressSchema,
)


class CRUDOrder(CRUDBase[Order, CreateOrderSchema, UpdateOrderAddressSchema]):
    """CRUD операции с заказами."""

    async def create_order(
        self, db: AsyncSession, user_id: UUID
    ) -> ReadOrderSchema:
        """Создать новый заказ из корзины пользователя."""
        new_order = Order(user_id=user_id, status_id=1)
        # "Создан" по умолчанию
        db.add(new_order)
        await db.flush()

        cart_items = (
            (await db.execute(select(Cart).filter(Cart.user_id == user_id)))
            .scalars()
            .all()
        )
        if not cart_items:
            raise HTTPException(status_code=400, detail='Корзина пуста')

        order_fireworks = [
            OrderFirework(
                order_id=new_order.id,
                firework_id=item.firework_id,
                amount=item.amount,
                price_per_unit=item.price_per_unit,
            )
            for item in cart_items
        ]
        db.add_all(order_fireworks)
        await db.commit()
        await db.refresh(
            new_order, attribute_names=['order_fireworks', 'status']
        )
        return ReadOrderSchema(
            id=new_order.id,
            status=new_order.status.status_text,
            user_address_id=new_order.user_address_id,
            order_fireworks=[
                OrderFireworkSchema.from_orm(fw)
                for fw in new_order.order_fireworks
            ],
            user_id=new_order.user_id,
        )

    async def repeat_order(
        self, db: AsyncSession, user_id: UUID, order_id: int
    ) -> ReadOrderSchema:
        """Повторить существующий заказ."""
        old_order = await db.get(Order, order_id)  # Используем lazy='selectin'
        if not old_order or old_order.user_id != user_id:
            raise HTTPException(status_code=404, detail='Заказ не найден')

        new_order = Order(
            user_id=user_id,
            status_id=1,
            user_address_id=old_order.user_address_id,
        )
        db.add(new_order)
        await db.flush()

        order_fireworks = [
            OrderFirework(
                order_id=new_order.id,
                firework_id=item.firework_id,
                amount=item.amount,
                price_per_unit=item.price_per_unit,
            )
            for item in old_order.order_fireworks
        ]
        db.add_all(order_fireworks)
        await db.commit()
        await db.refresh(
            new_order, attribute_names=['order_fireworks', 'status']
        )
        return ReadOrderSchema(
            id=new_order.id,
            status=new_order.status.status_text,
            user_address_id=new_order.user_address_id,
            order_fireworks=[
                OrderFireworkSchema.from_orm(fw)
                for fw in new_order.order_fireworks
            ],
            user_id=new_order.user_id,
        )

    async def get_orders_by_user(
        self, db: AsyncSession, user_id: UUID
    ) -> List[ReadOrderSchema]:
        """Получить список всех заказов пользователя."""
        query = select(Order).filter(Order.user_id == user_id)
        result = await db.execute(query)
        orders = result.scalars().all()  # Убрано unique(), так как нет JOIN-ов
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

    async def update_order_address(
        self,
        db: AsyncSession,
        user_id: UUID,
        user_address_id: UUID,
        order_id: int,
    ) -> ReadOrderSchema:
        """Обновить адрес заказа."""
        query = select(Order).filter(
            Order.id == order_id, Order.user_id == user_id
        )
        order = (await db.execute(query)).scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail='Заказ не найден')
        order.user_address_id = user_address_id
        await db.commit()
        await db.refresh(order, attribute_names=['order_fireworks', 'status'])
        return ReadOrderSchema(
            id=order.id,
            status=order.status.status_text,
            user_address_id=order.user_address_id,
            order_fireworks=[
                OrderFireworkSchema.from_orm(fw)
                for fw in order.order_fireworks
            ],
            user_id=order.user_id,
        )

    async def update_order_status(
        self, db: AsyncSession, user_id: UUID, status_id: int, order_id: int
    ) -> ReadOrderSchema:
        """Обновить статус заказа."""
        query = select(Order).filter(
            Order.id == order_id, Order.user_id == user_id
        )
        order = (await db.execute(query)).scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail='Заказ не найден')
        order.status_id = status_id
        await db.commit()
        await db.refresh(order, attribute_names=['order_fireworks', 'status'])
        return ReadOrderSchema(
            id=order.id,
            status=order.status.status_text,
            user_address_id=order.user_address_id,
            order_fireworks=[
                OrderFireworkSchema.from_orm(fw)
                for fw in order.order_fireworks
            ],
            user_id=order.user_id,
        )

    async def delete_order(
        self, db: AsyncSession, user_id: UUID, order_id: int
    ) -> bool:
        """Удалить заказ."""
        query = select(Order).filter(
            Order.id == order_id, Order.user_id == user_id
        )
        order = (await db.execute(query)).scalar_one_or_none()
        if not order or order.status_id != 1:
            return False
        await db.delete(order)
        await db.commit()
        return True


crud_order = CRUDOrder(Order)
