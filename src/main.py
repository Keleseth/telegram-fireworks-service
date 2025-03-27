from contextlib import asynccontextmanager

from fastapi import FastAPI

# from src.database import alembic_models  # noqa
from sqlalchemy.orm import configure_mappers

from src.admin.config import setup_admin
from src.api.v1.router import main_router
from src.config import settings
from src.utils.scheduler.scheduler import setup_scheduler, shutdown_scheduler

configure_mappers()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(
    title=settings.app_title,
    description=settings.description,
    lifespan=lifespan,
)
setup_admin(app)
app.router.include_router(main_router)


def main():
    """Функция запустит управляющую функцию. Для доступа извне."""
    pass


if __name__ == '__main__':
    main()
