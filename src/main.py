from fastapi import FastAPI

from src.api.v1.router import main_router

# from app.core.config import settings
# from app.core.init_db import create_first_superuser

# app = FastAPI(title=settings.app_title)
app = FastAPI()

app.include_router(main_router)


# @app.on_event('startup')
# async def startup():
#     await create_first_superuser()
