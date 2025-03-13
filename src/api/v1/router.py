from fastapi import APIRouter

from src.api.v1.endpoints.product import router as product_router

main_router = APIRouter()

main_router.include_router(product_router)
