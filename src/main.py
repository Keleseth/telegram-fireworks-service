from fastapi import FastAPI

from src.api.v1.router import main_router
from src.config import settings

app = FastAPI(title=settings.app_title, description=settings.description)

app.include_router(main_router)


def main():
    """Функция запустит управляющую функцию. Для доступа извне."""
    pass


if __name__ == 'main':
    main()
