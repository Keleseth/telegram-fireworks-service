import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo,
)

from src.models import Newsletter, User

PHOTO_FORMATS = ('.jpg', '.jpeg', '.png')
VIDEO_FORMATS = ('.mp4', '.mov')
TELEGRAM_MEDIA_LIMIT = 10


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

    # Создаем клавиатуру с тегами
    if newsletter.tags:
        keyboard = [
            [
                InlineKeyboardButton(
                    tag.name, callback_data=f'newsletter_tag_{tag.name}'
                )
            ]
            for tag in newsletter.tags
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        reply_markup = None

    # Формируем медиагруппу
    media_group = []
    media_urls = [media.media_url for media in newsletter.mediafiles][
        :TELEGRAM_MEDIA_LIMIT
    ]
    for media_url in media_urls:
        if media_url.endswith(PHOTO_FORMATS):
            media_group.append(InputMediaPhoto(media=media_url, caption=None))
        elif media_url.endswith(VIDEO_FORMATS):
            media_group.append(InputMediaVideo(media=media_url, caption=None))

    for user in users:
        if not user.telegram_id or user.is_admin:
            continue

        try:
            if media_group:
                # Отправляем медиагруппу
                await bot.send_media_group(
                    chat_id=user.telegram_id, media=media_group
                )
                # Отправляем кнопки отдельным сообщением
            if reply_markup:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=f'{newsletter.content}\nТеги:',
                    reply_markup=reply_markup,
                )
        except Exception as e:
            logging.error(f'User {user.id}: {str(e)}')
            continue

    # Обновляем статус рассылки
    newsletter.switch_send = True
    await session.commit()
