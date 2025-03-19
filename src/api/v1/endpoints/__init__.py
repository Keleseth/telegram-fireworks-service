from .activity import router as activity_router
from .address import router as address_router
from .cart import router as cart_router
from .favorite import router as favorite_router
from .order import router as order_router
from .payment import router as payment_router
from .product import router as product_router
from .user import router as user_router

__all__ = [
    activity_router,
    address_router,
    cart_router,
    favorite_router,
    order_router,
    payment_router,
    product_router,
    user_router,
]
