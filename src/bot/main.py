import asyncio
import logging

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from src.bot import config

# from src.bot.handlers.catalog import catalog_menu, catalog_register
from src.bot.handlers.order_history import order_history
from src.bot.handlers.order_history import (
    register_handlers as register_order_history,
)
from src.bot.handlers.place_order import (
    register_handlers as register_place_order,
)
from src.bot.handlers.promotions import promotions_handler
from src.bot.keyboards import keyboard_main, orders_summary_keyboard
from src.bot.utils import API_BASE_URL, get_user_id_from_telegram

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            'Добро пожаловать в телеграм бот Joker Fireworks! '
            'Для входа в меню введите /menu'
        ),
    )


async def menu(update: Update, context: CallbackContext) -> None:
    reply_markup = InlineKeyboardMarkup(keyboard_main)
    await update.message.reply_text(
        'Выберите пункт меню:', reply_markup=reply_markup
    )


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    option = query.data

    if option == 'back':
        reply_markup = InlineKeyboardMarkup(keyboard_main)
        await query.edit_message_text(
            text='Выберите пункт меню:', reply_markup=reply_markup
        )
    # elif option == 'catalog':
    #    await catalog_menu(update, context)
    elif option == 'promotions' or option.startswith((
        'promo_page_',
        'promo_detail_',
        'promo_back',
    )):
        await promotions_handler(update, context)
    elif option == 'orders':
        user_id = await get_user_id_from_telegram(update)
        if not user_id:
            await query.edit_message_text('Пользователь не найден.')
            return

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{API_BASE_URL}/orders/me',
                headers={'user-id': str(user_id)},
            )
            if response.status_code != 200:
                await query.edit_message_text('Ошибка при загрузке заказов.')
                return
            orders = response.json()

        if not orders:
            await query.edit_message_text(
                'У вас пока нет заказов.',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('Назад', callback_data='back')]
                ]),
            )
            return

        active_orders = len([
            o for o in orders if o['status'] not in ['Delivered', 'Cancelled']
        ])
        last_order = max(orders, key=lambda x: x['id'])
        # Предполагаем, что id увеличивается
        last_order_id = last_order['id']
        last_order_status = last_order['status']

        summary_text = (
            '📦 *Ваши заказы*\n'
            f'🔢 Активных: {active_orders}\n'
            f'📅 Последний: #{last_order_id} ({last_order_status})\n'
            'Выберите действие:'
        )
        reply_markup = InlineKeyboardMarkup(
            orders_summary_keyboard(last_order_id)
        )
        await query.edit_message_text(summary_text, reply_markup=reply_markup)
    elif option == 'show_all_orders':
        await order_history(update, context)


def main() -> None:
    print(f'Loaded TOKEN: {config.TOKEN}')
    application = ApplicationBuilder().token(config.TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    menu_handler = CommandHandler('menu', menu)
    application.add_handler(menu_handler)

    register_order_history(application)
    # Регистрация хэндлеров из order_history.py
    register_place_order(application)
    # Регистрация хэндлеров из place_order.py

    button_handler = CallbackQueryHandler(button)
    application.add_handler(button_handler)

    application.run_polling()


if __name__ == '__main__':
    asyncio.run(main())
