from fastapi import APIRouter

from src.api.v1.endpoints import (
    address_router,
    bot_info_router,
    cart_router,
    custom_admin_router,
    discount_router,
    favorite_router,
    order_router,
    product_router,
    user_router,
)

main_router = APIRouter()

main_router.include_router(product_router, tags=['Продукция'])
main_router.include_router(order_router, tags=['Заказы'])
main_router.include_router(discount_router, tags=['Акции'])
main_router.include_router(address_router, tags=['Адреса'])
main_router.include_router(cart_router, tags=['Корзина'])
main_router.include_router(user_router, tags=['Пользователи'])
main_router.include_router(favorite_router, tags=['Избранные'])
main_router.include_router(bot_info_router, tags=['Информация о боте'])
main_router.include_router(custom_admin_router, tags=['Кастомная админка'])
