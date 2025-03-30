from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.crud.newsletter import newsletter_crud
from src.database.db_dependencies import get_async_session
from src.utils.scheduler.send_newsletter import send_newsletter_to_users


async def check_newsletters(session: AsyncSession):
    """Проверяет рассылки и отправляет их, если наступило время.

    Параметры функции:
        1) session (AsyncSession) - сессия базы данных.
    """
    all_newsletters_unsett = await newsletter_crud.get_all_unsett_newslatter(
        session
    )
    current_time = datetime.now()
    if all_newsletters_unsett is None:
        return
    for newsletter in all_newsletters_unsett:
        if (
            newsletter.datetime_send <= current_time
            and current_time - newsletter.datetime_send <= timedelta(days=1)
            and newsletter.canceled is False
        ):
            filtered_users = (
                await newsletter_crud.filtered_users_for_newsletter(
                    newsletter=newsletter,
                    session=session,
                )
            )
            # TODO проверочная функция отправки рассылки самостоятельно.
            # TODO заменить на передачу данных в телеграм-бот и рассылку юзерам
            #  в цикле. За основу можно брать функцию send_newsletter_to_users.
            await send_newsletter_to_users(
                newsletter=newsletter,
                users=filtered_users,
                session=session,
                bot_token=settings.telegram_token,
            )


# Инициализация планировщика
scheduler = AsyncIOScheduler()


async def check_newsletters_wrapper() -> None:
    """Асинхронная обёртка для проверки и отправки рассылок через планировщик.

    Этот метод используется планировщиком (APScheduler) для выполнения
    задачи "check_newsletters" с заданным интервалом времени.
    Он отвечает за создание асинхронной сессии базы данных,
    передачу её в "check_newsletters" и корректное
    закрытие сессии после выполнения.

    Логика работы:
    1. Создаёт асинхронную сессию базы данных через "get_async_session()".
    2. Вызывает "check_newsletters(session)" для проверки и отправки рассылок.
    3. Закрывает сессию базы данных после выполнения,
       даже если произошла ошибка.

    Метод автоматически вызывается планировщиком.
    """
    async for session in get_async_session():
        try:
            await check_newsletters(session)
        finally:
            await session.close()


def setup_scheduler():
    """Функция, которая настраивает планировщик для проверки рассылок."""
    scheduler.add_job(
        check_newsletters_wrapper,
        'interval',
        seconds=10,
    )
    scheduler.start()


def shutdown_scheduler():
    """Функция останавливающая планировщик."""
    if scheduler.running:
        scheduler.shutdown()
