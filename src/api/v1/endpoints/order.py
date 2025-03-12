from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.order import crud_order
from src.database.db_dependencies import get_async_session
from src.schemas.order import (
    BaseOrderSchema,
    CreateOrderSchema,
    DeleteOrderSchema,
    ReadOrderSchema,
    UpdateOrderSchema,
)

router = APIRouter()

# TODO: Реализовать функцию для проверки источника запроса
# (например, через middleware или заголовки)


@router.post('/orders/', response_model=ReadOrderSchema)
async def create_new_order(
    order_data: CreateOrderSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Создание нового заказа."""
    return await crud_order.create_order(session, order_data)


@router.post('/orders/me', response_model=List[ReadOrderSchema])
async def get_my_orders(
    data: BaseOrderSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение списка заказов текущего пользователя."""
    return await crud_order.get_orders_by_user(session, data.telegram_id)


@router.post('/orders/get', response_model=ReadOrderSchema)
async def get_order(
    data: DeleteOrderSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение заказа по его идентификатору.

    Если он принадлежит пользователю.
    """
    orders = await crud_order.get_orders_by_user(session, data.telegram_id)
    order = next((o for o in orders if o.id == data.order_id), None)
    if order is None:
        raise HTTPException(status_code=404, detail='Заказ не найден')
    return order


@router.post('/orders/update', response_model=ReadOrderSchema)
async def update_existing_order(
    order_data: UpdateOrderSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновление данных заказа, если он принадлежит пользователю."""
    if not order_data.order_fireworks and order_data.user_address_id is None:
        raise HTTPException(
            status_code=400, detail='Нет данных для обновления'
        )
    updated_order = await crud_order.update_order(
        session, order_data, order_data.order_id
    )
    if updated_order is None:
        raise HTTPException(
            status_code=400, detail='Невозможно обновить заказ'
        )
    return updated_order


@router.post('/orders/delete')
async def delete_existing_order(
    data: DeleteOrderSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаление заказа, если он принадлежит пользователю."""
    deleted = await crud_order.delete_order(session, data)
    if not deleted:
        raise HTTPException(status_code=400, detail='Невозможно удалить заказ')
    return {'detail': 'Заказ успешно удален'}
