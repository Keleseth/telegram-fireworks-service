from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Bot

from src.crud.user import user_crud
from src.models import Newsletter, User


async def send_newsletter_to_users(
    newsletter: Newsletter,
    users: List[User],
    session: AsyncSession,
    bot_token: str,
):
    """Отправляет рассылку отфильтрованным пользователям через Telegram.

    Параметры:
        1) newsletter (Newsletter) - объект рассылки;
        2) users (List[User]) - Список пользователей,
           которым отправляется рассылка;
        3) session (AsyncSession) - сессия базы данных;
        4) bot_token (str) - токен Telegram-бота.
    """
    bot = Bot(token=bot_token)

    media_links = '\n'.join([
        media.media_url for media in newsletter.mediafiles
    ])
    full_message = newsletter.content
    if media_links:
        full_message = f'{newsletter.content}\n\nМедиафайлы:\n{media_links}'
    for user in users:
        if user.telegram_id:
            try:
                await bot.send_message(
                    chat_id=user.telegram_id, text=full_message
                )
            except Exception:
                continue
    newsletter.switch_send = True
    await session.commit()
    admins = await user_crud.get_all_users_admin(session=session)
    for admin in admins:
        if admin.telegram_id:
            try:
                await bot.send_message(
                    chat_id=admin.telegram_id,
                    text=f'Рассылка {newsletter.id} успешно отправлена! '
                    f'Отправлено {len(users)} пользователям.',
                )
            except Exception:
                continue
