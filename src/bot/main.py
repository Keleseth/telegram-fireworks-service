import asyncio
import logging

from telegram import InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from src.bot import config
from src.bot.handlers.bot_info import show_bot_info
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

    application.run_polling()


if __name__ == '__main__':
    asyncio.run(main())
