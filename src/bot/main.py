import asyncio
import logging

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from src.bot import config
from src.bot.handlers.bot_info import show_bot_info
from src.bot.handlers.catalog import catalog_menu, catalog_register
from src.bot.handlers.promotions import promotions_handler
from src.bot.keyboards import keyboard_main

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


async def menu(update: Update, contex: CallbackContext) -> None:
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
    elif option == 'catalog':
        await catalog_menu(update, context)
    elif option == 'promotions' or option.startswith((
        'promo_page_',
        'promo_detail_',
        'promo_back',
    )):
        await promotions_handler(update, context)
    elif option == 'bot_info':
        await show_bot_info(update, context)


def main() -> None:
    print(f'Loaded TOKEN: {config.TOKEN}')
    application = ApplicationBuilder().token(config.TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    menu_handler = CommandHandler('menu', menu)
    application.add_handler(menu_handler)

    catalog_register(application)

    button_handler = CallbackQueryHandler(button)
    application.add_handler(button_handler)

    application.run_polling()


if __name__ == '__main__':
    asyncio.run(main())
