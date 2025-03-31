from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes

SELECT_FILTERS_TITLE = 'Внимание! Фильтры активированы 🚀'

SELECT_FILTERS_CALLBACK = 'select_filters'


async def apply_filtering(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton(
                '⚡ Подобрать товары', callback_data='parameters'
            ),
            InlineKeyboardButton('🛡️ В главное меню', callback_data='back'),
        ]
    ]
    await query.edit_message_text(
        text=SELECT_FILTERS_TITLE, reply_markup=InlineKeyboardMarkup(keyboard)
    )


def setup_select_filters(application: ApplicationBuilder):
    application.add_handler(
        CallbackQueryHandler(
            apply_filtering, pattern=f'^{SELECT_FILTERS_CALLBACK}$'
        )
    )
