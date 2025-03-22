import asyncio
import logging
from datetime import datetime
from decimal import Decimal

import pandas as pd
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.models.media import FireworkMedia, Media
from src.models.product import Category, Firework
from src.models.property import FireworkProperty

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = Settings()


async def load_data(session: AsyncSession):
    try:
        # 1. Чтение CSV файла
        df = pd.read_csv(
            "price.csv",
            delimiter=",",
            quotechar='"',
            encoding="utf-8",
            thousands=',',
            keep_default_na=False
        )
        logger.info("CSV файл успешно прочитан")

        # 2. Обработка категорий
        category_map = await process_categories(session, df)

        # 3. Загрузка фейерверков
        firework_map = await process_fireworks(session, df, category_map)

        # 4. Загрузка медиа
        await process_media(session, df, firework_map)

        await session.commit()
        logger.info("Все данные успешно загружены")

    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при загрузке данных: {str(e)}")
        raise


def convert_number(value: str) -> int | None:
    """Конвертирует строковые числа с запятыми в int."""
    if not value or pd.isna(value):
        return None
    try:
        # Заменяем запятые на точки и конвертируем в float
        return int(float(value.replace(",", ".")))
    except (ValueError, TypeError) as e:
        logger.error(f"Ошибка конвертации числа '{value}': {str(e)}")
        return None


async def process_categories(session: AsyncSession, df: pd.DataFrame) -> dict:
    """Обработка иерархии категорий."""
    categories = {}
    default_category_name = "товары без категории"
    default_category_id = 1  # ID дефолтной категории

    # Проверяем, существует ли категория с id=1
    existing_category = await session.get(Category, default_category_id)
    if not existing_category:
        # Если категория с id=1 не существует, создаем её
        stmt = (
            pg_insert(Category)
            .values(id=default_category_id, name=default_category_name)
            .on_conflict_do_nothing()
        )
        await session.execute(stmt)
        logger.info(
            f"Создана дефолтная категория: {default_category_name} "
            f"(id={default_category_id})"
        )

    # Добавляем дефолтную категорию в словарь
    categories[default_category_name] = None

    # Собираем уникальные категории
    for _, row in (
            df[["Товарная группа", "Товарная подгруппа"]]
                    .drop_duplicates()
                    .iterrows()
    ):
        parent_name = row["Товарная группа"]
        child_name = row["Товарная подгруппа"] or parent_name

        if parent_name not in categories:
            categories[parent_name] = None  # Родительская категория
        if child_name and child_name not in categories:
            categories[child_name] = parent_name

    # Загрузка в БД
    category_map = {}
    for name, parent_name in categories.items():
        # Вставляем родительскую категорию, если нужно
        if parent_name and parent_name not in category_map:
            parent_stmt = pg_insert(Category).values(
                name=parent_name
            ).on_conflict_do_nothing()
            await session.execute(parent_stmt)

        # Получаем ID родителя
        parent_id = category_map.get(parent_name) if parent_name else None

        # Вставляем категорию
        stmt = (
            pg_insert(Category)
            .values(name=name, parent_category_id=parent_id)
            .on_conflict_do_update(
                index_elements=["name"],
                set_=dict(parent_category_id=parent_id)
            )
            .returning(Category.id, Category.name)
        )
        result = await session.execute(stmt)
        category = result.first()
        category_map[name] = category.id

    await session.flush()
    logger.info(f"Загружено {len(category_map)} категорий")
    return category_map


async def process_fireworks(
        session: AsyncSession, df: pd.DataFrame, category_map: dict
) -> dict:
    """Обработка фейерверков."""
    firework_map = {}
    default_category_id = 1  # ID дефолтной категории

    # Список полей, которые уже обрабатываются
    # и не должны попадать в firework_property
    excluded_fields = {
        "Код",  # code
        "Артикул",  # article
        "Наименование",  # name
        "Единица измерения",  # measurement_unit
        "Кол-во зарядов",  # charges_count
        "Кол-во эффектов",  # effects_count
        "Описание — как на Рутуб",  # description
        "Размер изделия, мм",  # product_size
        "Материал упаковки",  # packing_material
        "За единицу, ₽",  # price
        "Калибр, \"",  # caliber
        "Фото",  # photo (обрабатывается отдельно)
        "Видео",  # video (обрабатывается отдельно)
        "Товарная группа",  # category (обрабатывается через category_map)
        "Товарная подгруппа", # subcategory (обрабатывается через category_map)
    }

    # Преобразование данных
    fireworks_data = []
    for _, row in df.iterrows():
        # Если "Товарная группа" отсутствует, используем дефолтную категорию
        if pd.isna(row["Товарная группа"]) or not row["Товарная группа"]:
            category_id = default_category_id
        else:
            # Иначе используем "Товарная подгруппа" или "Товарная группа"
            category_name = row["Товарная подгруппа"] or row["Товарная группа"]
            category_id = category_map.get(category_name, default_category_id)

        # Конвертация цены
        try:
            price = Decimal(str(row["За единицу, ₽"]).replace(",", "."))
        except (ValueError, TypeError):  # Указываем конкретные исключения
            price = Decimal("0.0")

        # Обработка калибра
        caliber = row.get('Калибр, "', '').strip()

        # Собираем данные для вставки в таблицу Firework
        firework_data = {
            "code": row["Код"],
            "article": row["Артикул"],
            "name": row["Наименование"],
            "measurement_unit": row["Единица измерения"],
            "charges_count": convert_number(row["Кол-во зарядов"]),
            "effects_count": convert_number(row["Кол-во эффектов"]),
            "description": row["Описание — как на Рутуб"],
            "product_size": row["Размер изделия, мм"],
            "packing_material": row["Материал упаковки"],
            "price": price,
            "category_id": category_id,
            "caliber": caliber,
        }

        # Вставляем фейерверк и получаем его ID
        stmt = (
            pg_insert(Firework)
            .values(**firework_data)
            .on_conflict_do_update(
                index_elements=["code"],
                set_=dict(
                    article=firework_data["article"],
                    name=firework_data["name"],
                    price=firework_data["price"],
                    category_id=firework_data["category_id"],
                    caliber=firework_data["caliber"],
                )
            )
            .returning(Firework.id, Firework.code)
        )
        result = await session.execute(stmt)
        fw = result.first()
        firework_id = fw.id
        firework_map[firework_data["code"]] = firework_id

        # Собираем все дополнительные свойства в одну строку
        additional_properties = []
        for column in df.columns:
            if (column not in excluded_fields
                    and pd.notna(row[column])
                    and row[column] != ""):
                # Проверяем наличие точки с запятой и заменяем её на запятую
                value = str(row[column]).replace(";", ",")
                additional_properties.append(f"{column}: {value}")

        # Объединяем дополнительные свойства через точку с запятой
        if additional_properties:
            properties_str = "; ".join(additional_properties)
            # Вставляем объединенные свойства в таблицу firework_property
            stmt = (
                pg_insert(FireworkProperty)
                .values(
                    firework_id=firework_id,
                    property_description=properties_str,
                )
                .on_conflict_do_nothing()
            )
            await session.execute(stmt)

    await session.flush()
    logger.info(f"Загружено {len(fireworks_data)} фейерверков")
    return firework_map


async def process_media(
        session: AsyncSession, df: pd.DataFrame, firework_map: dict
):
    """Обработка медиа-файлов и связей с фейерверками."""
    media_map = {}  # Кэш URL медиа -> ID
    firework_media_records = []

    # Собираем все медиа и связи
    for _, row in df.iterrows():
        fw_code = row["Код"]
        fw_id = firework_map.get(fw_code)
        if not fw_id:
            logger.warning(f"Фейерверк {fw_code} не найден, пропуск медиа")
            continue

        # Обрабатываем фото и видео
        for url, media_type in [(row["Фото"], "image"), (
                row["Видео"], "video"
        )]:
            if not url:
                continue

            # Добавляем медиа в кэш или получаем существующий ID
            if url not in media_map:
                stmt = (
                    pg_insert(Media)
                    .values(
                        media_url=url,
                        media_type=media_type,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    .on_conflict_do_update(
                        index_elements=["media_url"],
                        set_=dict(
                            media_type=media_type,
                            updated_at=datetime.now()
                        )
                    )
                    .returning(Media.id)
                )
                result = await session.execute(stmt)
                media_id = result.scalar_one()
                media_map[url] = media_id
            else:
                media_id = media_map[url]

            # Добавляем связь в firework_media
            firework_media_records.append({
                "firework_id": fw_id,
                "image_id": media_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })

    # Пакетная вставка связей
    if firework_media_records:
        await session.execute(
            pg_insert(FireworkMedia)
            .values(firework_media_records)
            .on_conflict_do_nothing()
        )

    await session.flush()
    logger.info(
        f"Загружено {len(media_map)} медиа и {len(
            firework_media_records)} связей"
    )


if __name__ == "__main__":
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker

    async def async_main():
        db_url = settings.database_url

        # Создаем движок и сессию
        engine = create_async_engine(db_url)
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        # Запускаем загрузку
        async with async_session() as session:
            await load_data(session)

        await engine.dispose()
        print("Загрузка завершена!")

    # Запуск асинхронного event loop
    asyncio.run(async_main())
