# Модуль с кнопками Акций и скидок для телеграм бота
# TODO: чтобы интегрировать логику работы кнопок в main.py,
# нужно просто импортировать главный обработчик promotions_handler
# и в файле main.py в функции button поместить условие:
# elif data == 'promotions' or data.startswith(
#   ('promo_page_', 'promo_detail_')
# ):
#   await promotions_handler(update, context)


from datetime import datetime

from aiohttp import ClientSession
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

API_URL = 'http://localhost'
ITEMS_PER_PAGE = 5


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
        # Показ деталей акции
        promo_id = int(data.split('_')[2])
        await show_promo_details(update, context, promo_id)
    elif data == 'promo_back':
        # Возврат к списку акций
        await show_promotions_list(update, context)


async def show_promotions_list(
    update: Update, context: CallbackContext, page: int = 1
):
    """Показать список акций с пагинацией."""
    try:
        async with ClientSession() as session:
            response = await session.post(
                f'{API_URL}/discounts',
                json={'telegram_id': update.effective_user.id},
            )
            discounts = await response.json()

        total_pages = (len(discounts) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        start_idx = (page - 1) * ITEMS_PER_PAGE
        current_discounts = discounts[start_idx : start_idx + ITEMS_PER_PAGE]

        buttons = []
        for discount in current_discounts:
            end_date = datetime.fromisoformat(discount['end_date']).strftime(
                '%d.%m.%Y'
            )
            buttons.append([
                InlineKeyboardButton(
                    f'{discount["name"]} (до {end_date})',
                    callback_data=f'promo_detail_{discount["id"]}',
                )
            ])

        # Пагинация
        if len(discounts) > ITEMS_PER_PAGE:
            pagination = []
            if page > 1:
                pagination.append(
                    InlineKeyboardButton(
                        '◀️', callback_data=f'promo_page_{page - 1}'
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
                        '▶️', callback_data=f'promo_page_{page + 1}'
                    )
                )
            buttons.append(pagination)

        # Навигация
        buttons.append([
            InlineKeyboardButton('🔙 Назад', callback_data='back'),
            InlineKeyboardButton('🏠 Главная', callback_data='back'),
        ])

        text = '🎁 Акции и скидки:\n\n' + '\n'.join(
            f'• {d["name"]} - {d["description"]}' for d in current_discounts
        )

        await update.callback_query.edit_message_text(
            text=text, reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception:
        await handle_error(update, context)


async def show_promo_details(
    update: Update, context: CallbackContext, promo_id: int
):
    """Показать товары акции."""
    try:
        async with ClientSession() as session:
            response = await session.post(
                f'{API_URL}/discounts/{promo_id}',
                json={'telegram_id': update.effective_user.id},
            )
            fireworks = await response.json()
        # кнопки возвращают id фейерверка
        buttons = [
            [
                InlineKeyboardButton(
                    f'{f["name"]} - {f["price"]}₽',
                    callback_data=f'firework_{f["id"]}',
                )
            ]
            for f in fireworks
        ]

        buttons.append([
            InlineKeyboardButton(
                '🔙 К списку акций', callback_data='promotions'
            ),
            InlineKeyboardButton('🏠 Главная', callback_data='back'),
        ])

        await update.callback_query.edit_message_text(
            text='🎆 Акционные товары:',
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    except Exception:
        await handle_error(update, context)


async def handle_error(update: Update, context: CallbackContext):
    error_text = '⚠️ Произошла ошибка. Попробуйте позже.'
    await update.callback_query.edit_message_text(text=error_text)
