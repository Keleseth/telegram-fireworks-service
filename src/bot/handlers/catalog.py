"""Файл с обработчиками кнопок для каталога."""

import os
import ssl
import tempfile
from http import HTTPStatus
from typing import Any, Callable, Union

import aiohttp
import certifi
from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.bot.bot_messages import build_firework_card
from src.bot.utils import croling_content
from src.schemas.cart import UserIdentificationSchema

TEXT_FILTER = filters.TEXT & ~filters.COMMAND

(
    NAME,
    CHARGES_COUNT,
    CATEGORIES,
    ARTICLE,
    TAGS,
    MIN_RPICE,
    MAX_RPICE,
    ORDER_BY,
    APPLY,
    CANCEL,
) = range(10)

TELEGRAM_MEDIA_LIMIT = 10
PHOTO_FORMATS = ('.jpg', '.jpeg', 'png')
VIDEO_FORMATS = ('.mp4', '.mov')

FIREWORK_CARD = """
🎆 *{name}* 🎆
────────────────
💰 Цена: {price} ₽
🏷️ Акции: {discounts}
📝 Описание: {description}
────────────────
🏷️ Категория: {category_id}
🏷️ Теги: {tags}
────────────────
⚖️ Единица измерения: {measurement_unit}
📦 Размер продукта: {product_size}
📦 Упаковочный материал: {packing_material}
💥 Количество зарядов: {charges_count}
✨ Количество эффектов: {effects_count}
🔢 Артикул: `{article}`
────────────────
"""

FIREWORK_SHORT_CARD = """
🎆 {name} 🎆
────────────────
💰 Цена: {price} ₽
🏷️ Акции: {discounts}
"""

DISCOUNTS_LINE = """
🏷️ Скидки: {discounts}
"""

CATEGORY_CARD = """
💥 {name}
"""

CATALOG_CALLBACK = 'catalog'
ALL_PRODUCTS_CALLBACK = 'all_products'
ALL_CATEGORIES_CALLBACK = 'all_categories'
PARAMETERS_CALLBACK = 'parameters'
MAIN_MENU_CALLBACK = 'back'
ADD_TO_CART_CALLBACK = 'add_to_cart_{id}'
ADD_TO_FAVORITE_CALLBACK = 'add_to_favorite_{id}'
APPLY_FILTERS_CALLBACK = 'apply_filters'
CANCEL_FILTERS_CALLBACK = 'cancel_filters'

CATALOG_MESSAGE = '🎆 Каталог продуктов'
SUCCESS_ADD_MESSAGE_TO_CART = '✅ В корзине'
SUCCESS_ADD_MESSAGE_TO_FAVORITE = '✅ В избранном'
ALL_CATEGORIES_MESSAGE = '📋 Список категорий'
ALL_PRODUCTS_MESSAGE = '✨ Все товары'
CATEGORY_MESSAGE = '✨ Категории'
PARAMETERS_MESSAGE = '✨ Подбор по параметрам'
NEXT_PAGINATION_MESSAGE = '➡️ Следующая'
PREV_PAGINATION_MESSAGE = '⬅️ Предыдущая'
SKIP_MESSAGE = '⏭️ Пропустить'
CATALOG_BACK_MESSAGE = '📋 В каталог'
ADD_TO_CART_MESSAGE = '🛒 В корзину'
ADD_TO_FAVORITE_MESSAGE = '💥 В избранное'
MAIN_MENU_BACK_MESSAGE = '🏠 В главное меню'
NAVIGATION_MESSAGE = '🤖 Навигация'
BAD_REQUEST_MESSAGE = 'Ошибка❗ Код: {code}. Вернуться в меню каталога:'
READ_MORE_MESSAGE = '📖 Подробнее'


EMPTY_QUERY_MESSAGE = 'По вашему запросу ничего не найдено ⚠️'
EMPTY_DESCRIPTION_MESSAGE = 'Описание в разработке'
EMPTY_PRICE_MESSAGE = 'Цена за товар не указана'
EMPTY_TAGS_MESSAGE = 'Для товара теги не указаны'
EMPTY_PACKING_MATERIAL_MESSAGE = 'Материал упаковки не указан'
EMPTY_DISCOUNS_MESSAGE = 'Скоро появятся 🎆'

PRODUCT_PAGINATE_CALLBACK_DATA = 'pg-pr_{url}'
CATEGORY_PAGINATE_CALLBACK_DATA = 'pg-cat_{url}'
PRODUCT_FILTER_PAGINATE_CALLBACK_DATA = 'pg-pr-filter_{url}'

CLIENT_CONNECTION_ERROR = '❗Ошибка соединения❗'
ADD_TO_CART_ERROR = 'Ошибка добавления товара в корзину ❗'
ADD_TO_FAVORITE_ERROR = 'Ошибка добавления товара в избранное ❗'

WRITE_NAME_MESSAGE = '✏️ Укажите название товара:'
WRITE_CHARGES_COUNT = '✏️ Укажите количество зарядов:'
WRITE_CATEGORIES = '✏️ Укажите название категорий через пробел:'
WRITE_ARTICLE = '✏️ Укажите артикул:'
WRITE_TAGS = '📝 Укажите теги через пробел:'
WRITE_MIN_PRICE = '💰 Укажите минимальную цену: 📉'
WRITE_MAX_PRICE = '💰 Укажите максимальную цену: 📈'
WRITE_ORDER_BY = '📝 Укажите поля для сортировки:'
APPLY_FILTERS_BUTTON = '✅ Применить'
CANCEL_FILTERS_BUTTON = '❌ Отменить'
APPLY_FILTERS_MESSAGE = 'Применить полученные фильтры? 💎'
CANCEL_FILTERS_MESSAGE = 'Фильтрация отменена! ❌'

NOT_NUMERIC_TYPE_OF_CHARGES_COUNT_ERROR = (
    '🔢 Количество зарядов должно быть целым положительным числом!'
    ' Попробуйте ввести еще раз ☘️'
)
NOT_NUMERIC_TYPE_OF_PRICE_ERROR = (
    '🔢 Цена должна быть положительным числом! Попробуйте ввести еще раз ☘️'
)


catalog_navigation_keyboard = [
    [
        InlineKeyboardButton(
            ALL_PRODUCTS_MESSAGE, callback_data=ALL_PRODUCTS_CALLBACK
        )
    ],
    [
        InlineKeyboardButton(
            CATEGORY_MESSAGE, callback_data=ALL_CATEGORIES_CALLBACK
        )
    ],
    [
        InlineKeyboardButton(
            PARAMETERS_MESSAGE, callback_data=PARAMETERS_CALLBACK
        )
    ],
    [
        InlineKeyboardButton(
            MAIN_MENU_BACK_MESSAGE, callback_data=MAIN_MENU_CALLBACK
        )
    ],
]

keyboard_back = [
    [
        InlineKeyboardButton(
            MAIN_MENU_BACK_MESSAGE, callback_data=MAIN_MENU_CALLBACK
        )
    ]
]

filters_keyboard = [
    [
        InlineKeyboardButton(
            APPLY_FILTERS_BUTTON, callback_data=APPLY_FILTERS_CALLBACK
        )
    ],
    [
        InlineKeyboardButton(
            CANCEL_FILTERS_BUTTON, callback_data=CANCEL_FILTERS_CALLBACK
        )
    ],
]

main_menu_back_button = InlineKeyboardButton(
    MAIN_MENU_BACK_MESSAGE, callback_data=MAIN_MENU_CALLBACK
)

ssl_context = ssl.create_default_context(cafile=certifi.where())


def build_category_card(fields: dict, full_info: bool = True) -> str:
    """Заполняет карточку категории."""
    return CATEGORY_CARD.format(
        name=fields['name'],
        id=fields['id'],
        parent_category_id=fields['parent_category_id'],
    )


def build_filter_params_keyboard(filter_param_name: str):
    """Функция для построения клавиатуры.

    Кнопки:
        1. назад.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                MAIN_MENU_BACK_MESSAGE,
                callback_data=f'back_to_{filter_param_name}',
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def build_back_keyboard(
    message: str, back_point: str
) -> list[InlineKeyboardButton]:
    """Строит клавиатуру с кнопкой `назад`."""
    return [[go_back_button(message, back_point)]]


def go_back_button(message: str, back_point: str):
    return InlineKeyboardButton(message, callback_data=f'back_to_{back_point}')


def add_to_cart_button(firework_id: str):
    return InlineKeyboardButton(
        ADD_TO_CART_MESSAGE, callback_data=f'add_to_cart_{firework_id}'
    )


def add_to_favorite_button(firework_id: str):
    return InlineKeyboardButton(
        ADD_TO_FAVORITE_MESSAGE, callback_data=f'add_to_favorite_{firework_id}'
    )


def firework_read_more_button(firework_url: str):
    return InlineKeyboardButton(
        READ_MORE_MESSAGE, callback_data=f'firework_{firework_url}'
    )


def category_read_more_button(category_card: int, category_url: str):
    return InlineKeyboardButton(
        category_card, callback_data=f'categories_fireworks_{category_url}'
    )


def build_show_all_products_keyboard(
    firework_id: str,
) -> list[InlineKeyboardButton]:
    """Функция для построения клавиатуры.

    Кнопки:
        1. В корзину.
        2. В избранное.
    """
    firework_url = f'http://nginx:8000/fireworks/{firework_id}'
    return [
        [add_to_cart_button(firework_id), add_to_favorite_button(firework_id)],
        [firework_read_more_button(firework_url)],
    ]


def build_read_more_about_keyboard(firework_id: str) -> None:
    return [
        [add_to_cart_button(firework_id), add_to_favorite_button(firework_id)],
        [go_back_button(CATALOG_BACK_MESSAGE, CATALOG_CALLBACK)],
    ]


def build_show_all_categories_keyboard(
    category_card: int, category_id: str
) -> list[InlineKeyboardButton]:
    """Функция для построения клавиатуры.

    Кнопки:
        1. В корзину.
        2. В избранное.
    """
    return [[category_read_more_button(category_card, category_id)]]


def build_read_more_keyboard(category_id: str) -> list[InlineKeyboardButton]:
    return [
        [
            InlineKeyboardButton(
                READ_MORE_MESSAGE,
                callback_data=f'categories_fireworks_{category_id}',
            )
        ]
    ]


async def add_to_cart(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()
    try:
        async with aiohttp.ClientSession() as session:
            telegram_id = update.effective_user.id
            firework_id = int(query.data.split('_')[-1])
            async with session.post(
                'http://nginx:8000/user/cart',
                json=dict(
                    create_data=dict(amount=1, firework_id=firework_id),
                    user_ident=UserIdentificationSchema(
                        telegram_id=telegram_id
                    ).model_dump(),
                ),
            ):
                new_keyboard = [
                    [
                        InlineKeyboardButton(
                            SUCCESS_ADD_MESSAGE_TO_CART,
                            callback_data=ADD_TO_CART_CALLBACK.format(
                                id=firework_id
                            ),
                        ),
                        add_to_favorite_button(firework_id),
                    ],
                    [go_back_button(CATALOG_BACK_MESSAGE, CATALOG_CALLBACK)],
                ]
                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(new_keyboard)
                )
    except Exception:
        await query.message.reply_text(ADD_TO_CART_ERROR)


async def add_to_favorite(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()
    try:
        async with aiohttp.ClientSession() as session:
            # TODO добавить свое id
            # telegram_id = int(query.data)
            telegram_id = update.effective_user.id
            firework_id = int(query.data.split('_')[-1])
            async with session.post(
                'http://nginx:8000/favorites',
                json=dict(telegram_id=telegram_id, firework_id=firework_id),
            ):
                new_keyboard = [
                    [
                        add_to_cart_button(firework_id),
                        InlineKeyboardButton(
                            SUCCESS_ADD_MESSAGE_TO_FAVORITE,
                            callback_data=ADD_TO_FAVORITE_CALLBACK.format(
                                id=firework_id
                            ),
                        ),
                    ],
                    [go_back_button(CATALOG_BACK_MESSAGE, CATALOG_CALLBACK)],
                ]
                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(new_keyboard)
                )
    except Exception:
        await query.message.reply_text(ADD_TO_FAVORITE_ERROR)


async def catalog_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Создает каталог продуктов."""
    query = update.callback_query
    await query.answer()
    if context.chat_data.get(update.effective_chat.id, 'empty') == 'empty':
        context.chat_data[update.effective_chat.id] = []
    else:
        await catalog_delete_messages_from_memory(update, context)
        context.chat_data[update.effective_chat.id] = []
    await send_callback_message(
        query,
        update,
        context,
        CATALOG_MESSAGE,
        reply_markup=InlineKeyboardMarkup(catalog_navigation_keyboard),
    )


async def get_direct_yandex_url(public_url: str) -> str | None:
    api_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download'
    async with aiohttp.ClientSession() as session:
        async with session.get(
            api_url, params={'public_key': public_url}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get('href')
            print(f'⚠️ Ошибка получения href: {resp.status}')
    return None


async def download_yandex_image(public_url: str) -> str | None:
    direct_url = await get_direct_yandex_url(public_url)
    if not direct_url:
        print('❌ Не удалось получить прямую ссылку.')
        return None

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(direct_url) as resp:
                if resp.status == 200:
                    suffix = '.jpg' if '.jpg' in public_url else '.png'
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=suffix
                    ) as tmp_file:
                        tmp_file.write(await resp.read())
                        return tmp_file.name
                print(f'❌ Ошибка скачивания файла: {resp.status}')
        except Exception as e:
            print(f'❌ Исключение при скачивании: {e}')
    return None


PHOTO_FORMATS = ('.jpg', '.jpeg', '.png')
VIDEO_FORMATS = ('.mp4', '.mov')


async def show_media(
    update: Update, context: ContextTypes.DEFAULT_TYPE, media_list: list[dict]
):
    media_group = []
    temp_files = []  # пути к временным файлам

    for media in media_list[:10]:  # ограничение Telegram
        url = media['media_url']
        # async with aiohttp.ClientSession() as session:
        # async with session.post(
        #     f'http://127.0.0.1:8000/converted_media/{media["id"]}'
        # ) as response:
        #     data = await response.json()
        #     with open(file_path, 'rb') as f:  # noqa: ASYNC230
        #     if media_type == 'image':
        #         media_group.append(InputMediaPhoto(media=f.read()))
        media_type = media['media_type']

        if 'disk.yandex.ru' in url:
            file_path = await download_yandex_image(url)
            if not file_path:
                continue
            temp_files.append(file_path)
            with open(file_path, 'rb') as f:  # noqa: ASYNC230
                if media_type == 'image':
                    media_group.append(InputMediaPhoto(media=f.read()))
        else:
            continue

    if media_group:
        media_messages = await context.bot.send_media_group(
            chat_id=update.effective_chat.id, media=media_group
        )
        # Сохраняем message_id всех отправленных сообщений с фото
        media_ids = [msg.message_id for msg in media_messages]
        await add_messages_to_memory(update, context, *media_ids)

    # Удаляем временные файлы
    for path in temp_files:
        os.remove(path)


async def send_callback_message(
    query: CallbackQuery,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    content: str,
    reply_markup: InlineKeyboardMarkup | None,
    add_to_chat_data: bool = True,
    parse_mode: str = None,
) -> Message:
    """Отправляет сообщение в Markdown2 формате."""
    message = await query.message.reply_text(
        content, parse_mode=parse_mode, reply_markup=reply_markup
    )
    if add_to_chat_data:
        await add_messages_to_memory(update, context, message.id)
    return message


async def add_messages_to_memory(
    update: Update, context: ContextTypes.DEFAULT_TYPE, message_id: Message
):
    if update.effective_chat.id not in context.chat_data:
        context.chat_data[update.effective_chat.id] = []

    context.chat_data[update.effective_chat.id].append(message_id)


async def catalog_delete_messages_from_memory(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    try:
        for message_id in context.chat_data[update.effective_chat.id].copy():
            await context.bot.delete_message(
                chat_id=update.effective_chat.id, message_id=message_id
            )
            context.chat_data[update.effective_chat.id].remove(message_id)
    except Exception:
        print('Ошибка')


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
    """Базовая функция для возвращения списка объектов с пагинацией."""
    query = update.callback_query
    await query.answer()
    next_page_url = previous_page_url = None
    if context.chat_data[update.effective_chat.id]:
        await catalog_delete_messages_from_memory(update, context)
    try:
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl_context)
        ) as session:
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
                        await send_callback_message(
                            query,
                            update,
                            context,
                            EMPTY_QUERY_MESSAGE,
                            reply_markup=None,
                        )
                    for obj in objects:
                        caption = build_object_card(obj, full_info=full_info)
                        if obj.get('media'):
                            await show_media(update, context, obj['media'])
                        await send_callback_message(
                            query,
                            update,
                            context,
                            escape_markdown_v2(caption),
                            reply_markup=InlineKeyboardMarkup(
                                object_keyboard_builder(obj['id'])
                            ),
                            parse_mode='MarkdownV2',
                        )
                    print(context.chat_data[update.effective_chat.id])
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
                        update,
                        context,
                        NAVIGATION_MESSAGE,
                        InlineKeyboardMarkup(global_keyboard),
                    )
                else:
                    await send_callback_message(
                        query,
                        update,
                        context,
                        croling_content(
                            BAD_REQUEST_MESSAGE.format(code=response.status)
                        ),
                        InlineKeyboardMarkup(keyboard_back),
                    )
    except Exception:
        await send_callback_message(
            query,
            update,
            context,
            CLIENT_CONNECTION_ERROR,
            InlineKeyboardMarkup(keyboard_back),
        )


async def show_all_products(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    url: str | None = 'http://nginx:8000/fireworks',
) -> None:
    """Возвращает весь список товаров."""
    global_keyboard = [
        [
            InlineKeyboardButton(
                CATALOG_BACK_MESSAGE, callback_data=CATALOG_CALLBACK
            ),
            InlineKeyboardButton(
                MAIN_MENU_BACK_MESSAGE, callback_data=MAIN_MENU_CALLBACK
            ),
        ]
    ]
    await get_paginated_response(
        update=update,
        context=context,
        url=url,
        method='POST',
        object_key='fireworks',
        object_keyboard_builder=build_show_all_products_keyboard,
        build_object_card=build_firework_card,
        global_keyboard=global_keyboard,
        paginate_callback_data_pattern=PRODUCT_PAGINATE_CALLBACK_DATA,
    )


async def read_more_about_product(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Возвращает подробную информацию о конкретном продукте."""
    query = update.callback_query
    await query.answer()
    # try:
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        url = query.data.split('_')[-1]
        async with session.get(url) as response:
            if response.status == HTTPStatus.OK:
                firework = await response.json()
                await query.edit_message_text(
                    build_firework_card(firework, full_info=True),
                    reply_markup=InlineKeyboardMarkup(
                        build_read_more_about_keyboard(firework['id'])
                    ),
                    parse_mode='MarkdownV2',
                )
            else:
                await send_callback_message(
                    query,
                    update,
                    context,
                    BAD_REQUEST_MESSAGE.format(code=response.status),
                    InlineKeyboardMarkup(keyboard_back),
                    add_to_chat_data=False,
                )
    # except Exception:
    #     await send_callback_message(
    #         query,
    #         update,
    #         context,
    #         CLIENT_CONNECTION_ERROR,
    #         InlineKeyboardMarkup(keyboard_back),
    #     )


async def show_all_categories(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    url: str | None = 'http://nginx:8000/categories',
) -> None:
    """Возвращает все категории."""
    query = update.callback_query
    await query.answer()
    next_page_url = previous_page_url = None
    global_keyboard = [
        [go_back_button(CATALOG_BACK_MESSAGE, CATALOG_CALLBACK)]
    ]
    if context.chat_data[update.effective_chat.id]:
        await catalog_delete_messages_from_memory(update, context)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == HTTPStatus.OK:
                    data = await response.json()
                    categories = data['categories']
                    if not categories:
                        await query.message.reply_text(EMPTY_QUERY_MESSAGE)
                    keyboard = [
                        [
                            category_read_more_button(
                                build_category_card(category), category['id']
                            )
                        ]
                        for category in categories
                    ]
                    await send_callback_message(
                        query,
                        update,
                        context,
                        ALL_CATEGORIES_MESSAGE,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                    )
                    next_page_url = data['next_page_url']
                    previous_page_url = data['previous_page_url']
                    if next_page_url:
                        global_keyboard.append([
                            InlineKeyboardButton(
                                NEXT_PAGINATION_MESSAGE,
                                callback_data=(
                                    CATEGORY_PAGINATE_CALLBACK_DATA.format(
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
                                    CATEGORY_PAGINATE_CALLBACK_DATA.format(
                                        url=previous_page_url
                                    )
                                ),
                            )
                        ])
                    message = await send_callback_message(
                        query,
                        update,
                        context,
                        NAVIGATION_MESSAGE,
                        InlineKeyboardMarkup(global_keyboard),
                    )
                    print(message.id)
                else:
                    await send_callback_message(
                        query,
                        update,
                        context,
                        BAD_REQUEST_MESSAGE.format(code=response.status),
                        InlineKeyboardMarkup(keyboard_back),
                    )
    except Exception:
        await send_callback_message(
            query,
            update,
            context,
            CLIENT_CONNECTION_ERROR,
            InlineKeyboardMarkup(keyboard_back),
        )


async def show_categories_fireworks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    url: str | None = (
        'http://nginx:8000/fireworks/by_category/{category_id}'
    ),
) -> None:
    """Возвращает товары определенной категории."""
    query = update.callback_query
    await query.answer()
    category_id = query.data.split('_')[-1]
    await get_paginated_response(
        update=update,
        context=context,
        url=url.format(category_id=category_id),
        object_key='fireworks',
        object_keyboard_builder=build_show_all_products_keyboard,
        build_object_card=build_firework_card,
        global_keyboard=build_back_keyboard(
            CATALOG_BACK_MESSAGE, CATALOG_CALLBACK
        ),
        paginate_callback_data_pattern=PRODUCT_PAGINATE_CALLBACK_DATA,
    )


async def back_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок `назад`."""
    query = update.callback_query
    await query.answer()
    target_point = query.data.split('_')[-1]
    if target_point == CATALOG_CALLBACK:
        print(888)
        await catalog_menu(update, context)
    elif target_point == 'main-menu':
        print(999)
        if context.chat_data[update.effective_chat.id]:
            await catalog_delete_messages_from_memory(update, context)
    else:
        await query.message.reply_text('Пока в разработке /menu')


async def pagination_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Обработчик кнопок `вперед` и `назад` для пагинации."""
    query = update.callback_query
    await query.answer()
    target_pagination_point, url = query.data.split('_')
    if target_pagination_point == 'pg-pr':
        await show_all_products(update, context, url)
    elif target_pagination_point == 'pg-cat':
        await show_all_categories(update, context, url)
    elif target_pagination_point == 'pg-pr-filter':
        await apply_filters(
            update, context, url, request_data=context.user_data['filter']
        )


def build_filter_params_keyboard(handler_name: str) -> InlineKeyboardMarkup:
    """Универсальная клавиатура для пропуска."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                SKIP_MESSAGE, callback_data=f'skip_{handler_name}'
            )
        ]
    ])


async def handle_filter_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    next_step: int,
    next_question: str,
    field_name: str,
    next_field_name: str,
    value: Any = None,
):
    write_to_chat_data = False
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message_edit = query.edit_message_text
    else:
        message_edit = update.message.reply_text
        write_to_chat_data = True
    if value:
        context.user_data['filter'][field_name] = value
    message = await message_edit(
        next_question,
        reply_markup=build_filter_params_keyboard(next_field_name),
    )
    if write_to_chat_data:
        user_message = update.message.message_id
        context.chat_data[update.effective_chat.id].append(user_message)
        await add_messages_to_memory(update, context, message.id)
    return next_step


async def check_float_and_int_type(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    next_question: str,
    next_step: int,
    current_step: int,
    field_name: str,
    next_field_name: str,
    checked_value: str,
    needed_type: Union[int, float],
    error_message: str,
):
    """Проверяет checked_value на числовой тип."""
    try:
        value = needed_type(checked_value)
        if value < 0:
            raise Exception()
        return await handle_filter_step(
            update,
            context,
            next_step=next_step,
            next_question=next_question,
            field_name=field_name,
            next_field_name=next_field_name,
            value=value,
        )
    except Exception:
        await update.message.reply_text(error_message)
        return current_step


async def selection_by_parameters(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    print(999)
    if context.chat_data.get(update.effective_chat.id, 'empty') == 'empty':
        context.chat_data[update.effective_chat.id] = []
    query = update.callback_query
    await query.answer()
    context.user_data['filter'] = dict()
    await send_callback_message(
        query,
        update,
        context,
        WRITE_NAME_MESSAGE,
        reply_markup=build_filter_params_keyboard('name'),
    )
    return NAME


async def select_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_filter_step(
        update,
        context,
        next_step=CHARGES_COUNT,
        next_question=WRITE_CHARGES_COUNT,
        field_name='name',
        next_field_name='charges_count',
        value=update.message.text,
    )


async def skip_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_filter_step(
        update,
        context,
        next_step=CHARGES_COUNT,
        next_question=WRITE_CHARGES_COUNT,
        field_name='name',
        next_field_name='charges_count',
        value=None,
    )


async def select_charges_count(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    return await check_float_and_int_type(
        update,
        context,
        next_step=CATEGORIES,
        current_step=CHARGES_COUNT,
        next_question=WRITE_CATEGORIES,
        field_name='charges_count',
        next_field_name='categories',
        checked_value=update.message.text,
        error_message=NOT_NUMERIC_TYPE_OF_CHARGES_COUNT_ERROR,
        needed_type=int,
    )


async def skip_charges_count(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    return await handle_filter_step(
        update,
        context,
        next_step=CATEGORIES,
        next_question=WRITE_CATEGORIES,
        field_name='charges_count',
        next_field_name='categories',
        value=None,
    )


async def select_categories(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    return await handle_filter_step(
        update,
        context,
        next_step=ARTICLE,
        next_question=WRITE_ARTICLE,
        field_name='categories',
        next_field_name='article',
        value=update.message.text.split(),
    )


async def skip_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_filter_step(
        update,
        context,
        next_step=ARTICLE,
        next_question=WRITE_ARTICLE,
        field_name='categories',
        next_field_name='article',
        value=None,
    )


async def select_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_filter_step(
        update,
        context,
        next_step=TAGS,
        next_question=WRITE_TAGS,
        field_name='article',
        next_field_name='tags',
        value=update.message.text.split(),
    )


async def skip_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_filter_step(
        update,
        context,
        next_step=TAGS,
        next_question=WRITE_TAGS,
        field_name='article',
        next_field_name='tags',
        value=None,
    )


async def select_tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_filter_step(
        update,
        context,
        next_step=MIN_RPICE,
        next_question=WRITE_MIN_PRICE,
        field_name='tags',
        next_field_name='min_price',
        value=update.message.text,
    )


async def skip_tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_filter_step(
        update,
        context,
        next_step=MIN_RPICE,
        next_question=WRITE_MIN_PRICE,
        field_name='tags',
        next_field_name='min_price',
        value=None,
    )


async def select_min_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await check_float_and_int_type(
        update,
        context,
        next_step=MAX_RPICE,
        current_step=MIN_RPICE,
        next_question=WRITE_MAX_PRICE,
        field_name='min_price',
        next_field_name='max_price',
        checked_value=update.message.text,
        error_message=NOT_NUMERIC_TYPE_OF_PRICE_ERROR,
        needed_type=float,
    )


async def skip_min_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_filter_step(
        update,
        context,
        next_step=MAX_RPICE,
        next_question=WRITE_MAX_PRICE,
        field_name='min_price',
        next_field_name='max_price',
        value=None,
    )


async def select_max_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await check_float_and_int_type(
        update,
        context,
        next_step=ORDER_BY,
        current_step=MAX_RPICE,
        next_question=WRITE_ORDER_BY,
        field_name='max_price',
        next_field_name='order_by',
        checked_value=update.message.text,
        error_message=NOT_NUMERIC_TYPE_OF_PRICE_ERROR,
        needed_type=float,
    )


async def skip_max_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_filter_step(
        update,
        context,
        next_step=ORDER_BY,
        next_question=WRITE_ORDER_BY,
        field_name='max_price',
        next_field_name='order_by',
        value=None,
    )


async def select_order_by(update: Update, context: ContextTypes.DEFAULT_TYPE):
    write_to_chat_data = False
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message_edit = query.edit_message_text
    else:
        message_edit = update.message.reply_text
        write_to_chat_data = True
    context.user_data['filter']['order_by'] = update.message.text.split()
    message = await message_edit(
        APPLY_FILTERS_MESSAGE,
        reply_markup=InlineKeyboardMarkup(filters_keyboard),
    )
    if write_to_chat_data:
        await add_messages_to_memory(update, context, message.id)
    return APPLY


async def skip_order_by(update: Update, context: ContextTypes.DEFAULT_TYPE):
    write_to_chat_data = False
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        message_edit = query.edit_message_text
    else:
        message_edit = update.message.reply_text
        write_to_chat_data = True
    message = await message_edit(
        APPLY_FILTERS_MESSAGE,
        reply_markup=InlineKeyboardMarkup(filters_keyboard),
    )
    if write_to_chat_data:
        await add_messages_to_memory(update, context, message.id)
    return APPLY


async def cancel_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if context.chat_data[update.effective_chat.id]:
        await catalog_delete_messages_from_memory(update, context)
    await send_callback_message(
        query,
        update,
        context,
        croling_content(CANCEL_FILTERS_MESSAGE),
        reply_markup=InlineKeyboardMarkup([
            [
                main_menu_back_button,
                go_back_button(CATALOG_MESSAGE, CATALOG_CALLBACK),
            ]
        ]),
    )
    return ConversationHandler.END


async def apply_filters(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    url: str = 'http://nginx:8000/fireworks',
    request_data: dict = None,
) -> None:
    if context.chat_data[update.effective_chat.id]:
        await catalog_delete_messages_from_memory(update, context)
    if not request_data:
        filter_data = context.user_data['filter']
    else:
        filter_data = request_data
    global_keyboard = [
        [
            InlineKeyboardButton(
                CATALOG_BACK_MESSAGE, callback_data=CATALOG_CALLBACK
            ),
            InlineKeyboardButton(
                MAIN_MENU_BACK_MESSAGE, callback_data=MAIN_MENU_CALLBACK
            ),
        ]
    ]
    await get_paginated_response(
        update=update,
        context=context,
        url=url,
        method='POST',
        object_key='fireworks',
        object_keyboard_builder=build_show_all_products_keyboard,
        build_object_card=build_firework_card,
        global_keyboard=global_keyboard,
        paginate_callback_data_pattern=PRODUCT_FILTER_PAGINATE_CALLBACK_DATA,
        request_data=filter_data,
    )
    return ConversationHandler.END


def setup_catalog_handler(application: ApplicationBuilder) -> None:
    application.add_handler(
        CallbackQueryHandler(pagination_handler, pattern='^pg-')
    )
    application.add_handler(
        CallbackQueryHandler(catalog_menu, pattern=f'^{CATALOG_CALLBACK}$')
    )
    application.add_handler(
        CallbackQueryHandler(
            show_all_products, pattern=f'^{ALL_PRODUCTS_CALLBACK}$'
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            show_all_categories, pattern=f'^{ALL_CATEGORIES_CALLBACK}$'
        )
    )
    application.add_handler(
        CallbackQueryHandler(read_more_about_product, pattern='^firework_')
    )
    application.add_handler(
        CallbackQueryHandler(
            show_categories_fireworks, pattern='^categories_fireworks_'
        )
    )
    application.add_handler(
        CallbackQueryHandler(back_button, pattern='^back_to_')
    )
    application.add_handler(
        CallbackQueryHandler(add_to_cart, pattern='^add_to_cart')
    )
    application.add_handler(
        CallbackQueryHandler(add_to_favorite, pattern='^add_to_favorite')
    )
    conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                selection_by_parameters, pattern=f'^{PARAMETERS_CALLBACK}$'
            )
        ],
        states={
            NAME: [
                MessageHandler(TEXT_FILTER, select_name),
                CallbackQueryHandler(skip_name, pattern='^skip_name$'),
            ],
            CHARGES_COUNT: [
                MessageHandler(TEXT_FILTER, select_charges_count),
                CallbackQueryHandler(
                    skip_charges_count, pattern='^skip_charges_count$'
                ),
            ],
            CATEGORIES: [
                MessageHandler(TEXT_FILTER, select_categories),
                CallbackQueryHandler(
                    skip_categories, pattern='^skip_categories$'
                ),
            ],
            ARTICLE: [
                MessageHandler(TEXT_FILTER, select_article),
                CallbackQueryHandler(skip_article, pattern='^skip_article$'),
            ],
            TAGS: [
                MessageHandler(TEXT_FILTER, select_tags),
                CallbackQueryHandler(skip_tags, pattern='^skip_tags$'),
            ],
            MIN_RPICE: [
                MessageHandler(TEXT_FILTER, select_min_price),
                CallbackQueryHandler(
                    skip_min_price, pattern='^skip_min_price$'
                ),
            ],
            MAX_RPICE: [
                MessageHandler(TEXT_FILTER, select_max_price),
                CallbackQueryHandler(
                    skip_max_price, pattern='^skip_max_price$'
                ),
            ],
            ORDER_BY: [
                MessageHandler(TEXT_FILTER, select_order_by),
                CallbackQueryHandler(skip_order_by, pattern='^skip_order_by$'),
            ],
            APPLY: [
                CallbackQueryHandler(
                    apply_filters, pattern=f'^{APPLY_FILTERS_CALLBACK}$'
                )
            ],
        },
        fallbacks=[
            CallbackQueryHandler(
                cancel_filters, pattern=f'^{CANCEL_FILTERS_CALLBACK}$'
            )
        ],
    )
    application.add_handler(conversation_handler)


def escape_markdown_v2(text: str) -> str:
    """Экранирует спецсимволы для MarkdownV2."""
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(
        f'\\{char}' if char in escape_chars else char for char in text
    )
