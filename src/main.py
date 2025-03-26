from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqladmin import Admin

# from src.database import alembic_models  # noqa
from sqlalchemy.orm import configure_mappers

from src.admin.config import get_sqladmin_auth

# from src.admin.config import setup_admin
from src.api.v1.router import main_router
from src.config import settings
from src.database.db_dependencies import engine

configure_mappers()

admin_app = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код, выполняемый при запуске приложения (startup)
    global admin_app
    auth_backend = await get_sqladmin_auth()
    admin_app = Admin(
        app=app,
        engine=engine,
        authentication_backend=auth_backend,
    )
    yield


app = FastAPI(
    title=settings.app_title,
    description=settings.description,
    lifespan=lifespan,
)
# setup_admin(app)
app.router.include_router(main_router)


def main():
    """Функция запустит управляющую функцию. Для доступа извне."""
    pass


if __name__ == '__main__':
    main()
