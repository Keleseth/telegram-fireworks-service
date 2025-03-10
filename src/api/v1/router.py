from fastapi import APIRouter

from src.api.v1.endpoints import (
    activity_router,
    address_router,
    cart_router,
    order_router,
    payment_router,
    product_router,
    user_router,
)

main_router = APIRouter()

main_router.include_router(
    activity_router,
    address_router,
    cart_router,
    order_router,
    payment_router,
    product_router,
    user_router,
)
