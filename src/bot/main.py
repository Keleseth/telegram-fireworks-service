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
from src.bot.handlers.catalog import catalog_menu, catalog_register
from src.bot.handlers.promotions import promotions_handler
from src.bot.handlers.users import UserManager
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
        await user_manager._send_main_menu(
            update, user_data.get('is_admin', False)
        )
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
    elif option.startswith(('promo_', 'promotions')):
        await promotions_handler(update, context)
    await user_manager.refresh_keyboard(update)


def main() -> None:
    print(f'Loaded TOKEN: {config.TOKEN}')
    application = ApplicationBuilder().token(config.TOKEN).build()
    application.user_manager = UserManager(application)

    # Регистрация обработчиков
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('menu', menu))
    catalog_register(application)
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()


if __name__ == '__main__':
    asyncio.run(main())
