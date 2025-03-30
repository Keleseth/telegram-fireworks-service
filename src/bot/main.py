import asyncio
import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.bot import config
from src.bot.handlers.bot_info import show_bot_info
from src.bot.handlers.cart import (
    change_quantity,
    checkout,
    clear_cart_handler,
    handle_new_quantity,
    remove_item,
    view_cart,
)
from src.bot.handlers.catalog import (
    catalog_menu,
    setup_catalog_handler,
)
from src.bot.handlers.favorites import setup_favorites_handler, show_favorites
from src.bot.handlers.newsletter import handle_newsletter_tag
from src.bot.handlers.promotions import promotions_handler
from src.bot.handlers.select_filters import (
    apply_filtering,
    setup_select_filters,
)
from src.bot.handlers.users import TelegramUserManager
from src.bot.keyboards import keyboard_main

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_manager = context.application.user_manager
    user_data = await user_manager.check_registration(update.effective_user.id)

    if user_data:
        await user_manager._send_main_menu(
            update,
        )
    else:
        await update.message.reply_text(
            'Добро пожаловать! Введите ваш возраст:',
            reply_markup=ReplyKeyboardRemove(),
        )


async def menu(update: Update, context: CallbackContext):
    user_manager = context.application.user_manager
    user_data = await user_manager.check_registration(update.effective_user.id)

    if user_data:
        await user_manager._send_main_menu(update)
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

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            'Добро пожаловать в телеграм бот Joker Fireworks! '
            'Для входа в меню введите /menu'
        ),
    )


keyboard_back = [[InlineKeyboardButton('Назад', callback_data='back')]]


async def menu(update: Update, context: CallbackContext):
    reply_markup = InlineKeyboardMarkup(keyboard_main)
    await update.message.reply_text(
        'Выберите пункт меню:', reply_markup=reply_markup
    )


async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    option = query.data

    if option == 'back':
        reply_markup = InlineKeyboardMarkup(keyboard_main)
        await query.edit_message_text(
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

    # await user_manager.refresh_keyboard(update)

    # TODO начало корзина - сделать общий обработчик
    elif option == 'cart':
        await view_cart(update, context)
    elif option == 'checkout':
        await checkout(update, context)
    elif option.startswith('change_item_'):
        item_id = option.split('_')[2]
        await change_quantity(update, context, item_id)
    elif option.startswith('remove_'):
        item_id = option.split('_')[1]
        await remove_item(update, context, item_id)
    elif option == 'clear_cart':
        await clear_cart_handler(update, context)
    # конец корзина
    else:
        reply_markup = InlineKeyboardMarkup(keyboard_back)
        await query.edit_message_text(
            text=f'Выбран пункт: {option}', reply_markup=reply_markup
        )


def main() -> None:
    print(f'Loaded TOKEN: {config.TOKEN}')
    application = ApplicationBuilder().token(config.TOKEN).build()
    application.user_manager = TelegramUserManager(application)

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    menu_handler = CommandHandler('menu', menu)
    application.add_handler(menu_handler)

    setup_catalog_handler(application)
    setup_favorites_handler(application)
    setup_select_filters(application)

    button_handler = CallbackQueryHandler(button)
    application.add_handler(button_handler)

    checkout_handler = CallbackQueryHandler(checkout, pattern='^checkout$')
    application.add_handler(checkout_handler)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_quantity)
    )
    application.add_handler(
        CallbackQueryHandler(remove_item, pattern='^remove_')
    )
    application.add_handler(
        CallbackQueryHandler(clear_cart_handler, pattern='clear_cart')
    )

    application.run_polling()


if __name__ == '__main__':
    asyncio.run(main())
