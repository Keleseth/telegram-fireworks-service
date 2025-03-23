import logging

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

from src.bot import config
from src.bot.handlers.catalog import catalog_menu, catalog_states
from src.bot.keyboards import keyboard_main, menu
from src.bot.states import MENU, SELECT_MENU_POSITION

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            'Добро пожаловать в телеграм бот Joker Fireworks! '
            'Для входа в меню введите /menu'
        )
    )
    return MENU


# async def menu(update: Update, context: CallbackContext):
#     if update.callback_query:
#         query = update.callback_query
#         await query.answer()
#         await query.edit_message_text(
#             text='Вы выбрали каталог',
#             reply_markup=InlineKeyboardMarkup(keyboard_main)
#         )
#     else:
#         await update.message.reply_text(
#             text='Вы выбрали каталог',
#             reply_markup=InlineKeyboardMarkup(keyboard_main)
#         )
#     return SELECT_MENU_POSITION


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text('Диалог отменен!')
    return ConversationHandler.END


async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    option = query.data
    if option == 'back':
        reply_markup = InlineKeyboardMarkup(keyboard_main)
        await query.edit_message_text(
            text='Выберите пункт меню:', reply_markup=reply_markup
        )
        return SELECT_MENU_POSITION
    if option == 'catalog':
        return await catalog_menu(update, context)
    # else:
    #     reply_markup = InlineKeyboardMarkup(keyboard_back)
    #     await query.edit_message_text(
    #         text=f'Выбран пункт: {option}', reply_markup=reply_markup
    #     )


# async def catalog_inline_handler(
#     update: Update,
#     context: CallbackContext
# ):
#     query = update.callback_query
#     await query.answer()
#     option = query.data
#     if option == 'all_catalog':
#         return await show_all_catalog(update, context)
#     elif option == 'categories':
#         return await show_categories(update, context)
#     elif option == 'parameters':
#         await query.edit_message_text('parameters')
#         return CATALOG
#     elif option == 'back_to_catalog':
#         return await catalog_menu(update, context)
#     else:
#         return await menu(update, context)


if __name__ == '__main__':
    application = ApplicationBuilder().token(config.TOKEN).build()

    # start_handler = CommandHandler('start', start)
    # application.add_handler(start_handler)

    # menu_handler = CATALOG
    # application.add_handler(menu_handler)

    main_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
                MENU: [CommandHandler('menu', menu)],
                SELECT_MENU_POSITION: [CallbackQueryHandler(button)],
                **catalog_states
            },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False
    )
    # application.add_handler(catalog_conversation_handler)
    application.add_handler(main_conversation_handler)

    # catalog_menu_handler = CallbackQueryHandler(catalog_menu)
    # application.add_handler(catalog_menu)

    # product_redister_handlers(application)

    application.run_polling()
