from http import HTTPStatus
from typing import Callable

import aiohttp
from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
    Update,
)
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

from src.bot.keyboards import keyboard_back

MARCDOWN_VERSION = 2

TELEGRAM_MEDIA_LIMIT = 10
PHOTO_FORMATS = ('.jpg', '.jpeg', 'png')
VIDEO_FORMATS = ('.mp4', '.mov')

NEXT_PAGINATION_MESSAGE = '➡️ Следующая'
PREV_PAGINATION_MESSAGE = '⬅️ Предыдущая'
EMPTY_QUERY_MESSAGE = 'По вашему запросу ничего не найдено ⚠️'
NAVIGATION_MESSAGE = '🤖 Навигация'
BAD_REQUEST_MESSAGE = 'Ошибка❗ Код: {code}. Вернуться в меню каталога:'
CLIENT_CONNECTION_ERROR = '❗Ошибка соединения❗'


def croling_content(content: str) -> str:
    return escape_markdown(content, version=MARCDOWN_VERSION)


async def send_callback_message(
    query: CallbackQuery,
    content: str,
    reply_markup: InlineKeyboardMarkup | None,
) -> Message:
    """Отправляет сообщение в Markdown2 формате."""
    return await query.message.reply_text(
        content, parse_mode='MarkdownV2', reply_markup=reply_markup
    )


async def show_media(
    query: CallbackQuery,
    context: ContextTypes.DEFAULT_TYPE,
    media_list: list[str],
):
    media_group = []
    media_urls = [media['media_url'] for media in media_list][
        :TELEGRAM_MEDIA_LIMIT
    ]
    for media_url in media_urls:
        if media_url.endswith(PHOTO_FORMATS):
            media_group.append(InputMediaPhoto(media=media_url, caption=None))
        elif media_url.endswith(VIDEO_FORMATS):
            media_group.append(InputMediaVideo(media=media_url, caption=None))
    await context.bot.send_media_group(
        chat_id=query.message.chat_id, media=media_group
    )


async def get_paginated_response(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    url: str,
    object_key: str,
    object_keyboard_builder: Callable[[str], list[InlineKeyboardButton]],
    build_object_card: Callable[[dict], str],
    global_keyboard: list[InlineKeyboardButton],
    paginate_callback_data_pattern: str,
    method: str = 'GET',
    full_info: bool = False,
    request_data: dict = None,
) -> None:
    """Базовая функция для возвращения списка продуктов с пагинацией."""
    query = update.callback_query
    await query.answer()
    next_page_url = previous_page_url = None
    try:
        async with aiohttp.ClientSession() as session:
            if method == 'POST':
                response_context_manager = await session.post(
                    url, json=request_data
                )
            else:
                response_context_manager = await session.get(url)
            async with response_context_manager as response:
                if response.status == HTTPStatus.OK:
                    data = await response.json()
                    objects = data[object_key]
                    if not objects:
                        await query.message.reply_text(EMPTY_QUERY_MESSAGE)
                    for obj in objects:
                        caption = build_object_card(obj, full_info=full_info)
                        if obj.get('media'):
                            await show_media(query, context, obj['media'])
                        await send_callback_message(
                            query,
                            caption,
                            reply_markup=InlineKeyboardMarkup(
                                object_keyboard_builder(obj['id'])
                            ),
                        )
                    next_page_url = data['next_page_url']
                    previous_page_url = data['previous_page_url']
                    if next_page_url:
                        global_keyboard.append([
                            InlineKeyboardButton(
                                NEXT_PAGINATION_MESSAGE,
                                callback_data=(
                                    paginate_callback_data_pattern.format(
                                        url=next_page_url
                                    )
                                ),
                            )
                        ])
                    if previous_page_url:
                        global_keyboard.append([
                            InlineKeyboardButton(
                                PREV_PAGINATION_MESSAGE,
                                callback_data=(
                                    paginate_callback_data_pattern.format(
                                        url=previous_page_url
                                    )
                                ),
                            )
                        ])
                    await send_callback_message(
                        query,
                        NAVIGATION_MESSAGE,
                        InlineKeyboardMarkup(global_keyboard),
                    )
                else:
                    await send_callback_message(
                        query,
                        croling_content(
                            BAD_REQUEST_MESSAGE.format(code=response.status)
                        ),
                        InlineKeyboardMarkup(keyboard_back),
                    )
    except Exception:
        await send_callback_message(
            query,
            CLIENT_CONNECTION_ERROR,
            InlineKeyboardMarkup(keyboard_back),
        )
