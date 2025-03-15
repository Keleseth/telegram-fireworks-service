from fastapi import FastAPI

# from src.database import alembic_models  # noqa
from sqlalchemy.orm import configure_mappers

from src.api.v1.router import main_router
from src.config import settings

configure_mappers()

app = FastAPI(title=settings.app_title, description=settings.description)

app.router.include_router(main_router)


def main():
    """Функция запустит управляющую функцию. Для доступа извне."""
    pass


if __name__ == '__main__':
    main()
