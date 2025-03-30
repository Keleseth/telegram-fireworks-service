"""Файл с обработчиками кнопок для каталога."""

from http import HTTPStatus

import aiohttp
from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
)
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes

from src.bot.keyboards import keyboard_back
from src.bot.utils import croling_content

FIREWORK_CARD = """
🎆 *{name}* 🎆
────────────────
🔢 **Код товара:** `{code}`
📏 **Единица измерения:** {measurement_unit}
📝 **Описание:** {description}
🏷️ **Категория:** {category_id}
📦 **Размер продукта:** {product_size}
📦 **Упаковочный материал:** {packing_material}
💥 **Количество зарядов:** {charges_count}
✨ **Количество эффектов:** {effects_count}
🔢 **Артикул:** `{article}`
────────────────
"""


CATEGORY_CARD = """
📂 *{name}*

🆔 **ID:** `{id}`
📂 **Родительская категория ID:** {parent_category_id}
"""


navigation_keyboard = [
    [InlineKeyboardButton('Весь каталог', callback_data='all_catalog')],
    [InlineKeyboardButton('Категории', callback_data='all_categories')],
    [InlineKeyboardButton('Подбор по параметрам', callback_data='parameters')],
    [InlineKeyboardButton('Назад', callback_data='back')],
]


def build_firework_card(fields: dict) -> str:
    """Заполняет карточку пролукта."""
    if not fields['description']:
        fields['description'] = croling_content('Описание в разработке')
    if not fields['price']:
        fields['price'] = croling_content('Цена за товар не указана')
    if not fields['tags']:
        fields['tags'] = croling_content('Для товара теги не указаны')
    if not fields['packing_material']:
        fields['packing_material'] = croling_content(
            'Материал упаковки не указан'
        )
    return FIREWORK_CARD.format(
        name=fields['name'],
        code=fields['code'],
        measurement_unit=fields['measurement_unit'],
        description=fields['description'],
        category_id=fields['category_id'],
        product_size=fields['product_size'],
        packing_material=fields['packing_material'],
        charges_count=fields['charges_count'],
        effects_count=fields['effects_count'],
        article=fields['article'],
    )


def build_category_card(fields: dict) -> str:
    """Заполняет карточку категории."""
    return CATEGORY_CARD.format(
        name=fields['name'],
        id=fields['id'],
        parent_category_id=fields['parent_category_id'],
    )


async def send_callback_message(
    query: CallbackQuery,
    content: str,
    reply_markup: InlineKeyboardMarkup | None,
) -> Message:
    """Отправляет сообщение в Markdown2 формате."""
    return await query.message.reply_text(
        content, parse_mode='MarkdownV2', reply_markup=reply_markup
    )


def build_filter_params_keyboard(filter_param_name: str):
    """Функция для построения клавиатуры.

    Кнопки:
        1. назад.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                'Назад', callback_data=f'back_to_{filter_param_name}'
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def build_back_keyboard(
    message: str, back_point: str
) -> list[InlineKeyboardButton]:
    """Строит клавиатуру с кнопкой `назад`."""
    return [
        [InlineKeyboardButton(message, callback_data=f'back_to_{back_point}')]
    ]


def build_cart_and_favorite_keyboard(
    firework_id: str,
) -> list[InlineKeyboardButton]:
    """Функция для построения клавиатуры.

    Кнопки:
        1. В корзину.
        2. В избранное.
    """
    return [
        [
            InlineKeyboardButton(
                'В корзину', callback_data=f'add_to_cart_{firework_id}'
            )
        ],
        [
            InlineKeyboardButton(
                'В избранное', callback_data=f'add_to_favorite_{firework_id}'
            )
        ],
    ]


async def catalog_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Создает каталог продуктов."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        'Каталог продуктов: ',
        reply_markup=InlineKeyboardMarkup(navigation_keyboard),
    )


async def show_all_products(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    url: str | None = 'http://127.0.0.1:8000/fireworks',
) -> None:
    """Возвращает весь список товаров."""
    query = update.callback_query
    await query.answer()
    if context.user_data.get('message_ids'):
        for message_id in context.user_data['message_ids']:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id, message_id=message_id
            )
    next_page_url = previous_page_url = None
    async with aiohttp.ClientSession() as session:
        async with session.post(url) as response:
            if response.status == HTTPStatus.OK:
                data = await response.json()
                fireworks = data['fireworks']
                message_ids = []
                for firework in fireworks:
                    message = await send_callback_message(
                        query,
                        build_firework_card(firework),
                        reply_markup=InlineKeyboardMarkup(
                            build_cart_and_favorite_keyboard(
                                firework_id=firework['id']
                            )
                        ),
                    )
                    message_ids.append(message.id)
                context.user_data['message_ids'] = message_ids
                if data.get('next_page_url'):
                    next_page_url = data['next_page_url']
                if data.get('previous_page_url'):
                    previous_page_url = data['previous_page_url']
            else:
                context.user_data['message_ids'] = message_ids
                await query.message.reply_text(
                    'Ошибка запроса. Вернуться в меню каталога:',
                    reply_markup=InlineKeyboardMarkup(keyboard_back),
                )
    keyboard = build_back_keyboard('В каталог', 'catalog')
    if next_page_url:
        keyboard.append([
            InlineKeyboardButton(
                'Вперёд', callback_data=f'pg-pr_{next_page_url}'
            )
        ])
    if previous_page_url:
        keyboard.append([
            InlineKeyboardButton(
                'Назад', callback_data=f'pg-pr_{previous_page_url}'
            )
        ])
    await query.message.reply_text(
        'Навигация:', reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def back_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок `назад`."""
    query = update.callback_query
    await query.answer()
    target_point = query.data.split('_')[-1]
    if target_point == 'catalog':
        await catalog_menu(update, context)
    else:
        await query.message.reply('Пока в разработке /menu')


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


async def show_all_categories(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    url: str | None = 'http://127.0.0.1:8000/categories',
) -> None:
    """Возвращает все категории."""
    query = update.callback_query
    await query.answer()
    if context.user_data.get('message_ids'):
        for message_id in context.user_data['message_ids']:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id, message_id=message_id
            )
    next_page_url = previous_page_url = None
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == HTTPStatus.OK:
                data = await response.json()
                categories = data['categories']
                message_ids = []
                for category in categories:
                    keyboard = [
                        [
                            InlineKeyboardButton(
                                'Подробнее',
                                callback_data=f'category_{category["id"]}',
                            )
                        ]
                    ]
                    message = await send_callback_message(
                        query,
                        build_category_card(category),
                        reply_markup=InlineKeyboardMarkup(keyboard),
                    )
                    message_ids.append(message.id)
                context.user_data['message_ids'] = message_ids
                if data.get('next_page_url'):
                    next_page_url = data['next_page_url']
                if data.get('previous_page_url'):
                    previous_page_url = data['previous_page_url']
            else:
                context.user_data['message_ids'] = message_ids
                await query.message.reply_text(
                    'Ошибка запроса. Вернуться в меню каталога:',
                    reply_markup=InlineKeyboardMarkup(keyboard_back),
                )
    keyboard = build_back_keyboard('В каталог', 'catalog')
    if next_page_url:
        keyboard.append([
            InlineKeyboardButton(
                'Вперёд', callback_data=f'pg-cat_{next_page_url}'
            )
        ])
    if previous_page_url:
        keyboard.append([
            InlineKeyboardButton(
                'Назад', callback_data=f'pg-cat_{previous_page_url}'
            )
        ])
    await query.message.reply_text(
        'Навигация:', reply_markup=InlineKeyboardMarkup(keyboard)
    )


# async def show_categories_inline_handler(
#     update: Update,
#     context: ContextTypes.DEFAULT_TYPE
# ):
#     """Обработчик кнопок show_categories."""
#     query = update.callback_query
#     await query.answer()
#     option = query.data
#     if option.startswith('category_'):
#         return await show_categories_fireworks(update, context)
#     return await show_all_categories(update, context)


async def show_categories_fireworks(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Возвращает товары определенной категории."""
    # category_id = update.callback_query.data.split('_')[-1]
    # TODO обращение к БД
    fireworks = ['Firework_category1', 'Firework_category2']
    for firework in fireworks:
        keyboard = [
            [
                InlineKeyboardButton(
                    'В корзину', callback_data=f'add_to_cart_{firework}'
                ),
                InlineKeyboardButton(
                    'В избранное', callback_data=f'add_to_favorite_{firework}'
                ),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text(
            firework, reply_markup=reply_markup
        )
    await update.callback_query.message.reply_text(
        'Вернуться к категориям:',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('Назад', callback_data='back_to_categories')]
        ]),
    )


def catalog_register(application: ApplicationBuilder) -> None:
    application.add_handler(
        CallbackQueryHandler(pagination_handler, pattern='^pg-')
    )
    application.add_handler(
        CallbackQueryHandler(catalog_menu, pattern='^catalog$')
    )
    application.add_handler(
        CallbackQueryHandler(show_all_products, pattern='^all_catalog$')
    )
    application.add_handler(
        CallbackQueryHandler(show_all_categories, pattern='^all_categories$')
    )
    application.add_handler(
        CallbackQueryHandler(back_button, pattern='^back_to_')
    )
