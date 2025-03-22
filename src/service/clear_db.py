import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import Settings

settings = Settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def clear_tables(session: AsyncSession) -> None:
    """Полная очистка всех связанных таблиц в правильном порядке."""
    try:
        # Порядок важен из-за foreign key constraints
        tables = [
            "firework_media",
            "media",
            "cart",
            "favoritefirework",
            "firework_tag",
            "fireworkdiscount",
            "firework_property",  # Добавляем новую таблицу
            "firework",
            "category",
            "tag"
        ]

        # Формируем SQL команду с использованием text()
        truncate_command = text(
            "TRUNCATE TABLE {} RESTART IDENTITY CASCADE;".format(
                ", ".join(tables)
            )
        )

        await session.execute(truncate_command)
        await session.commit()

        logger.info(f"Успешно очищены таблицы: {', '.join(tables)}")

    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка очистки таблиц: {str(e)}")
        raise


async def async_main():
    db_url = settings.database_url
    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession)

    async with async_session() as session:
        await clear_tables(session)


if __name__ == "__main__":

    asyncio.run(async_main())
