from src.api.v1.endpoints.activity import router as activity_router
from src.api.v1.endpoints.address import router as address_router
from src.api.v1.endpoints.bot_info import router as bot_info_router
from src.api.v1.endpoints.cart import router as cart_router
from src.api.v1.endpoints.custom_admin import router as custom_admin_router
from src.api.v1.endpoints.discounts import router as discount_router
from src.api.v1.endpoints.favorite import router as favorite_router
from src.api.v1.endpoints.order import router as order_router
from src.api.v1.endpoints.payment import router as payment_router
from src.api.v1.endpoints.product import router as product_router
from src.api.v1.endpoints.user import router as user_router

__all__ = [
    'activity_router',
    'address_router',
    'bot_info_router',
    'cart_router',
    'discount_router',
    'favorite_router',
    'order_router',
    'payment_router',
    'product_router',
    'user_router',
    'custom_admin_router',
]
