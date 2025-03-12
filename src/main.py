from fastapi import FastAPI
from sqlalchemy.orm import configure_mappers

from src.config import settings

configure_mappers()

app = FastAPI(title=settings.app_title, description=settings.description)


def main():
    """Функция запустит управляющую функцию. Для доступа извне."""
    pass


if __name__ == '__main__':
    main()
