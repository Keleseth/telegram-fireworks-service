# Модуль с кнопками Акций и скидок для телеграм бота
# TODO: чтобы интегрировать логику работы кнопок в main.py,
# нужно просто импортировать главный обработчик promotions_handler
# и в файле main.py в функции button поместить условие:
# elif data == 'promotions' or data.startswith(
#   ('promo_page_', 'promo_detail_')
# ):
#   await promotions_handler(update, context)


from datetime import datetime, timedelta
from decimal import Decimal

from aiohttp import ClientSession
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown

# Данные для тестов
MOCK_DISCOUNTS = [
    {
        'id': i,
        'type': f'Акция {i}',
        'description': f'Описание акции {i}',
        'end_date': (datetime.now() + timedelta(days=i)).isoformat(),
        'fireworks': list(range(i * 10, i * 10 + 7)),
    }
    for i in range(1, 11)
]
# Данные для тестов
MOCK_FIREWORKS = {
    i: {
        'id': i,
        'name': f'Фейерверк {i}',
        'price': Decimal(500 + i * 100),
        'description': f'Описание фейерверка {i}' if i % 2 == 0 else None,
        'code': f'FW{i:03}',
        'article': f'ART-{i:03}',
    }
    for i in range(1, 100)
}

API_URL = 'http://127.0.0.1:8000'

ITEMS_PER_PAGE = 3
PROMO_PER_PAGE = 5

FIREWORK_PROMO_CARD = """
🎆 *{name}* 🎆
────────────────
💵 **Цена:** {price}₽
📝 **Описание:** {description}
💥 **Зарядов:** {charges_count}
✨ **Эффектов:** {effects_count}
────────────────
"""


async def promotions_handler(update: Update, context: CallbackContext):
    """Главный обработчик для акций."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'promotions':
        # Первый вход в раздел акций
        await show_promotions_list(update, context)
    elif data.startswith('promo_page_'):
        # Обработка пагинации
        page = int(data.split('_')[2])
        await show_promotions_list(update, context, page)
    elif data.startswith('promo_detail_'):
        parts = data.split('_')
        promo_id = int(parts[2])
        page = int(parts[4]) if len(parts) > 4 else 1
        await show_promo_details(update, context, promo_id, page)


async def show_promotions_list(
    update: Update, context: CallbackContext, page: int = 1
):
    """Показать список акций с пагинацией."""
    try:
        async with ClientSession() as session:
            async with session.get(f'{API_URL}/discounts') as response:
                discounts = await response.json()

        total_pages = (len(discounts) + PROMO_PER_PAGE - 1) // PROMO_PER_PAGE
        start_idx = (page - 1) * PROMO_PER_PAGE
        current_discounts = discounts[start_idx : start_idx + PROMO_PER_PAGE]

        buttons = []
        for discount in current_discounts:
            end_date = datetime.fromisoformat(discount['end_date']).strftime(
                '%d.%m.%Y'
            )
            buttons.append([
                InlineKeyboardButton(
                    f'{discount["type"]} (до {end_date})',
                    callback_data=f'promo_detail_{discount["id"]}_page_1',
                )
            ])

        # Пагинация для акций
        if len(discounts) > PROMO_PER_PAGE:
            pagination = []
            if page > 1:
                pagination.append(
                    InlineKeyboardButton(
                        '◀️ Акции', callback_data=f'promo_page_{page - 1}'
                    )
                )
            pagination.append(
                InlineKeyboardButton(
                    f'{page}/{total_pages}', callback_data=' '
                )
            )
            if page < total_pages:
                pagination.append(
                    InlineKeyboardButton(
                        'Акции ▶️', callback_data=f'promo_page_{page + 1}'
                    )
                )
            buttons.append(pagination)

        # Кнопки навигации
        buttons.append([
            InlineKeyboardButton('🔙 Назад', callback_data='back'),
            InlineKeyboardButton('🏠 Главная', callback_data='back'),
        ])

        text = '🎁 Акции и скидки:\n\n' + '\n'.join(
            f'• {d["type"]} - {d["description"]}' for d in current_discounts
        )

        await update.callback_query.edit_message_text(
            text=text, reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as error:
        await handle_error(update, context)
        raise error


def build_promo_firework_card(fields: dict) -> str:
    """Заполняет упрощенную карточку для акций."""
    defaults = {
        'description': 'Описание отсутствует',
        'charges_count': 'Не указано',
        'effects_count': 'Не указано',
    }

    for field in defaults:
        if not fields.get(field):
            fields[field] = defaults[field]
    return FIREWORK_PROMO_CARD.format(
        name=fields['type'],
        price=fields['value'],
        description=fields['description'],
        charges_count=fields['charges_count'],
        effects_count=fields['effects_count'],
    )


async def show_promo_details(
    update: Update, context: CallbackContext, promo_id: int, page: int = 1
):
    """Показать товары акции с пагинацией и упрощенными карточками."""
    try:
        # Тестовые данные вместо API
        async with ClientSession() as session:
            async with session.get(f'{API_URL}/discounts') as response:
                all_fireworks = await response.json()

        # Пагинация
        total_pages = (
            len(all_fireworks) + ITEMS_PER_PAGE - 1
        ) // ITEMS_PER_PAGE
        start_idx = (page - 1) * ITEMS_PER_PAGE
        current_fireworks = all_fireworks[
            start_idx : start_idx + ITEMS_PER_PAGE
        ]

        # Удаляем предыдущие сообщения
        if 'promo_message_ids' in context.user_data:
            for msg_id in context.user_data['promo_message_ids']:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id, message_id=msg_id
                )

        message_ids = []
        for firework in current_fireworks:
            # Экранируем все текстовые поля
            escaped_firework = {
                key: escape_markdown(str(value), version=2)
                for key, value in firework.items()
            }

            msg = await update.callback_query.message.reply_text(
                text=build_promo_firework_card(escaped_firework),
                parse_mode='MarkdownV2',
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            'В корзину',
                            callback_data=f'add_to_cart_{firework["id"]}',
                        ),
                        InlineKeyboardButton(
                            'Подробнее',
                            callback_data=f'firework_{firework["id"]}',
                        ),
                    ]
                ]),
            )
            message_ids.append(msg.message_id)

        context.user_data['promo_message_ids'] = message_ids

        # Кнопки пагинации
        pagination_buttons = []
        if page > 1:
            pagination_buttons.append(
                InlineKeyboardButton(
                    '◀️',
                    callback_data=f'promo_detail_{promo_id}_page_{page - 1}',
                )
            )

        pagination_buttons.append(
            InlineKeyboardButton(f'{page}/{total_pages}', callback_data=' ')
        )

        if page < total_pages:
            pagination_buttons.append(
                InlineKeyboardButton(
                    '▶️',
                    callback_data=f'promo_detail_{promo_id}_page_{page + 1}',
                )
            )

        # Кнопки навигации
        nav_buttons = [
            InlineKeyboardButton(
                '🔙 К списку акций',
                callback_data=f'promo_page_{
                    context.user_data.get("current_promo_page", 1)
                }',
            ),
            InlineKeyboardButton('🏠 Главная', callback_data='back'),
        ]

        # Отправляем управляющее сообщение
        control_msg = await update.callback_query.message.reply_text(
            'Навигация:',
            reply_markup=InlineKeyboardMarkup([
                pagination_buttons,
                nav_buttons,
            ]),
        )
        context.user_data['control_message'] = control_msg.message_id

    except Exception as error:
        await handle_error(update, context)
        raise error


async def handle_error(update: Update, context: CallbackContext):
    error_text = '⚠️ Произошла ошибка. Попробуйте позже.'
    await update.callback_query.edit_message_text(text=error_text)
