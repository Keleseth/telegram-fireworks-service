from telegram import Update
from telegram.ext import (
    ContextTypes,
)

from src.bot.handlers.catalog import apply_filters


async def handle_newsletter_tag(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    # Разбиваем данные на части
    tag_name = query.data.split('_')[-1]
    await apply_filters(
        update=update, context=context, request_data={'tags': [tag_name]}
    )
