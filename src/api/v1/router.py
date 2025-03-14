from fastapi import APIRouter

from src.api.v1.endpoints import order_router

main_router = APIRouter()

main_router.include_router(order_router)
