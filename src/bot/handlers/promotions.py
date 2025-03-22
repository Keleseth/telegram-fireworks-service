from aiohttp import ClientSession
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

ITEMS_PER_PAGE = 5
API_URL = 'http://127.0.0.1'


def get_pagination_buttons(current_page: int, total_pages: int) -> list:
    buttons = []
    if current_page > 1:
        buttons.append(
            InlineKeyboardButton(
                '← Назад', callback_data=f'promo_page_{current_page - 1}'
            )
        )
    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton(
                'Вперед →', callback_data=f'promo_page_{current_page + 1}'
            )
        )
    return buttons


async def show_promotions_menu(
    update: Update, context: CallbackContext, page: int = 1
):
    query = update.callback_query
    if query:
        await query.answer()

    async with ClientSession() as session:
        async with session.post(
            f'{API_URL}/discounts',
            json={'telegram_id': update.effective_user.id},
        ) as response:
            discounts = await response.json()

    total_pages = (len(discounts) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start_idx = (page - 1) * ITEMS_PER_PAGE
    current_discounts = discounts[start_idx : start_idx + ITEMS_PER_PAGE]

    keyboard = []
    for discount in current_discounts:
        keyboard.append([
            InlineKeyboardButton(
                f'{discount["name"]} (до {discount["end_date"]})',
                callback_data=f'promo_detail_{discount["id"]}',
            )
        ])

    if len(discounts) > ITEMS_PER_PAGE:
        keyboard.append(get_pagination_buttons(page, total_pages))

    keyboard.append([
        InlineKeyboardButton('Назад', callback_data='back'),
        InlineKeyboardButton('Главное меню', callback_data='main_menu'),
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = '🎁 Акции и скидки:\n\n' + '\n'.join([
        f'• {d["name"]} - {d["description"]}' for d in current_discounts
    ])

    if query:
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=reply_markup,
        )


async def show_promotion_detail(
    update: Update, context: CallbackContext, promo_id: int
):
    query = update.callback_query
    await query.answer()

    async with ClientSession() as session:
        async with session.post(
            f'{API_URL}/discounts/{promo_id}',
            json={'telegram_id': update.effective_user.id},
        ) as response:
            fireworks = await response.json()

    keyboard = []
    for firework in fireworks:
        keyboard.append([
            InlineKeyboardButton(
                f'{firework["name"]} - {firework["price"]}₽',
                callback_data=f'firework_{firework["id"]}',
            )
        ])

    keyboard.append([
        InlineKeyboardButton('← К списку акций', callback_data='promo_page_1'),
        InlineKeyboardButton('Главное меню', callback_data='main_menu'),
    ])

    await query.edit_message_text(
        text='🎆 Акционные товары:',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_promotions_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data.startswith('promo_page_'):
        page = int(data.split('_')[2])
        await show_promotions_menu(update, context, page)
    elif data.startswith('promo_detail_'):
        promo_id = int(data.split('_')[2])
        await show_promotion_detail(update, context, promo_id)
