from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.crud.order import crud_order
from src.database.db_dependencies import get_async_session
from src.models.order import Order
from src.models.user import Cart
from src.schemas.order import (
    BaseOrderSchema,
    CreateOrderSchema,
    DeleteOrderSchema,
    ReadOrderSchema,
    UpdateOrderAddressSchema,
    UpdateOrderStatusSchema,
)

router = APIRouter(prefix='/orders', tags=['orders'])


@router.post('/', response_model=ReadOrderSchema)
async def create_new_order(
    order_data: CreateOrderSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Создать новый заказ.

    Инициализация заказа без адреса или повторение существующего заказа
    с адресом.
    """
    return await crud_order.create_order(session, order_data)


@router.post('/me', response_model=List[ReadOrderSchema])
async def get_my_orders(
    data: BaseOrderSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Получить список всех заказов пользователя."""
    return await crud_order.get_orders_by_user(session, data.telegram_id)


@router.post('/get', response_model=ReadOrderSchema)
async def get_order(
    data: DeleteOrderSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Получить заказ по его идентификатору.

    Возвращает информацию о заказе, если он принадлежит пользователю.
    """
    orders = await crud_order.get_orders_by_user(session, data.telegram_id)
    order = next((o for o in orders if o.id == data.order_id), None)
    if order is None:
        raise HTTPException(status_code=404, detail='Заказ не найден')
    return order


@router.patch('/{order_id}/address', response_model=ReadOrderSchema)
async def update_order_address(
    order_id: int,
    data: UpdateOrderAddressSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновить адрес заказа."""
    return await crud_order.update_order_address(session, data, order_id)


@router.patch('/{order_id}/status', response_model=ReadOrderSchema)
async def update_order_status(
    order_id: int,
    data: UpdateOrderStatusSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновить статус заказа."""
    return await crud_order.update_order_status(session, data, order_id)


@router.post('/{order_id}/to_cart')
async def move_order_to_cart(
    order_id: int,
    data: BaseOrderSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Переместить товары из заказа в корзину."""
    user_id = await crud_order.get_user_id_by_telegram_id(
        session, data.telegram_id
    )
    order = (
        await session.execute(
            select(Order).filter(
                Order.id == order_id, Order.user_id == user_id
            )
        )
    ).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail='Заказ не найден')
    for item in order.order_fireworks:
        session.add(
            Cart(
                user_id=user_id,
                firework_id=item.firework_id,
                amount=item.amount,
            )
        )
    await session.commit()
    return {'detail': 'Товары добавлены в корзину'}


@router.post('/delete')
async def delete_existing_order(
    data: DeleteOrderSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Удалить заказ."""
    deleted = await crud_order.delete_order(session, data)
    if not deleted:
        raise HTTPException(status_code=400, detail='Невозможно удалить заказ')
    return {'detail': 'Заказ успешно удалён'}
