import asyncio
import logging

import httpx
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from src.bot import config
from src.bot.handlers.bot_info import show_bot_info
from src.bot.handlers.cart import (
    checkout,
    clear_cart_handler,
    delete_cart_messages,
    handle_back_to_cart,
    remove_item,
    setup_cart_handler,
    view_cart,
)
from src.bot.handlers.catalog import (
    catalog_menu,
    setup_catalog_handler,
)
from src.bot.handlers.favorites import setup_favorites_handler, show_favorites
from src.bot.handlers.newsletter import handle_newsletter_tag

# from src.bot.handlers.catalog import catalog_menu, catalog_register
from src.bot.handlers.order_history import order_history
from src.bot.handlers.place_order import (
    register_handlers as register_place_order,
)
from src.bot.handlers.promotions import promotions_handler
from src.bot.handlers.select_filters import (
    apply_filtering,
    setup_select_filters,
)
from src.bot.handlers.users import TelegramUserManager
from src.bot.keyboards import keyboard_main, orders_summary_keyboard
from src.bot.utils import API_BASE_URL, get_user_id_from_telegram

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

keyboard_back = [[InlineKeyboardButton('Назад', callback_data='back')]]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_manager = context.application.user_manager
    return await user_manager.start(update, context)


async def menu(update: Update, context: CallbackContext):
    user_manager = context.application.user_manager
    user_data = await user_manager.check_registration(update.effective_user.id)

    if user_data:
        await user_manager.show_main_menu(update, context)
    else:
        await update.message.reply_text(
            'Пожалуйста, сначала зарегистрируйтесь через /start'
        )


async def button(update: Update, context: CallbackContext):
    user_manager = context.application.user_manager
    if not await user_manager.check_registration(update.effective_user.id):
        await update.message.reply_text(
            'Пожалуйста, сначала зарегистрируйтесь через /start'
        )
        return

    query = update.callback_query
    await query.answer()
    option = query.data
    print(f'Данные callback_query: {query.data}')

    if option == 'back':
        await delete_cart_messages(update, context)
        reply_markup = InlineKeyboardMarkup(keyboard_main)
        await query.message.reply_text(
            text='Выберите пункт меню:', reply_markup=reply_markup
        )
    elif option == 'catalog':
        await catalog_menu(update, context)
    elif option == 'product_filter':
        await apply_filtering(update, context)
    elif option == 'favorites':
        await show_favorites(update, context)
    elif option.startswith(('promo_', 'promotions')):
        await promotions_handler(update, context)
    elif option == 'bot_info':
        await show_bot_info(update, context)
    elif option.startswith(('newsletter_tag_',)):
        await handle_newsletter_tag(update, context)
    # TODO 126-138 добавит один обработчик для корзины
    elif option == 'cart':
        await view_cart(update, context)
    elif option == 'checkout':
        await checkout(update, context)
    elif option.startswith('remove_'):
        item_id = option.split('_')[1]
        await remove_item(update, context, item_id)
    elif option == 'clear_cart':
        await clear_cart_handler(update, context)
    # TODO добавить 1 обработчик для заказов
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
                json={'telegram_id': update.effective_user.id},
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

    # await user_manager.refresh_keyboard(update)


def main() -> None:
    print(f'Loaded TOKEN: {config.TOKEN}')
    application = ApplicationBuilder().token(config.TOKEN).build()
    application.user_manager = TelegramUserManager(application)
    # application.add_handler(conv_handler)

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    menu_handler = CommandHandler('menu', menu)
    application.add_handler(menu_handler)

    setup_catalog_handler(application)
    setup_favorites_handler(application)
    setup_select_filters(application)
    # register_order_history(application)
    # Регистрация хэндлеров из order_history.py
    register_place_order(application)
    # Регистрация хэндлеров из place_order.py
    setup_cart_handler(application)

    button_handler = CallbackQueryHandler(button)
    application.add_handler(button_handler)

    checkout_handler = CallbackQueryHandler(checkout, pattern='^checkout$')
    application.add_handler(checkout_handler)
    application.add_handler(
        CallbackQueryHandler(remove_item, pattern='^remove_')
    )
    application.add_handler(
        CallbackQueryHandler(clear_cart_handler, pattern='clear_cart')
    )
    application.add_handler(
        CallbackQueryHandler(handle_back_to_cart, pattern='^main-menu$')
    )

    # To poll
    application.run_polling()

    # Запуск вебхука

    # application.run_webhook(
    #     listen="0.0.0.0",
    #     port=8443,
    #     url_path="/webhook",
    #     webhook_url="https://jf-team2.rsateam.ru/webhook",
    # )


if __name__ == '__main__':
    asyncio.run(main())
