from fastapi import APIRouter

from src.api.v1.endpoints import cart_router

main_router = APIRouter()

# main_router.include_router(product_router)
main_router.include_router(cart_router)
