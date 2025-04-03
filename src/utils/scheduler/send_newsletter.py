import logging
from typing import List

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo,
    Update,
)
from telegram.ext import CallbackContext

from src.bot.handlers.catalog import build_firework_card
from src.models import Newsletter, User

API_URL = 'http://localhost:8000/fireworks'

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
                await bot.send_media_group(
                    chat_id=user.telegram_id, media=media_group
                )
            if reply_markup:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=f'{newsletter.content}\nТеги:',
                    reply_markup=reply_markup,
                )
        except Exception as e:
            logging.error(f'User {user.id}: {str(e)}')
            continue
    newsletter.switch_send = True
    await session.commit()


async def handle_tag_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    tag_name = query.data.replace('newsletter_tag_', '')
    params = {'offset': 0, 'limit': 10}
    json_data = {'tags': [tag_name]}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_URL, params=params, json=json_data
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as e:
        await query.edit_message_text(f'Ошибка при запросе данных: {str(e)}')
        return
    fireworks = data.get('fireworks', [])
    if not fireworks:
        await query.edit_message_text('По этому тегу ничего не найдено.')
        return
    for firework in fireworks:
        card_text = build_firework_card(firework, full_info=True)
        media_urls = firework.get('media_urls', [])
        if media_urls:
            media_group = []
            for idx, url in enumerate(media_urls[:TELEGRAM_MEDIA_LIMIT]):
                if url.endswith(PHOTO_FORMATS):
                    if idx == 0:
                        media_group.append(
                            InputMediaPhoto(
                                media=url,
                                caption=card_text,
                                parse_mode='Markdown',
                            )
                        )
                    else:
                        media_group.append(InputMediaPhoto(media=url))
                elif url.endswith(VIDEO_FORMATS):
                    if idx == 0:
                        media_group.append(
                            InputMediaVideo(
                                media=url,
                                caption=card_text,
                                parse_mode='Markdown',
                            )
                        )
                    else:
                        media_group.append(InputMediaVideo(media=url))
            if media_group:
                await context.bot.send_media_group(
                    chat_id=query.message.chat_id, media=media_group
                )
            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=card_text,
                    parse_mode='Markdown',
                )
        else:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=card_text,
                parse_mode='Markdown',
            )
