from aiohttp import ClientSession
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

BOT_INFO_CARD = """
🤖 *Информация о боте* 🤖
──────────────────────
{bot_info}

🏢 *О компании*:
{about_company}

📞 *Контакты*:
{contacts}
──────────────────────
"""

API_URL = 'http://app:8000'


def build_bot_info_card(fields: dict) -> str:
    """Формирует карточку информации о боте."""
    return BOT_INFO_CARD.format(
        bot_info=escape_markdown(
            fields.get('bot_info', 'Информация о боте'), version=2
        ),
        about_company=escape_markdown(
            fields.get('about_company', 'Информация о компании'), version=2
        ),
        contacts=escape_markdown(
            fields.get('contacts', 'Контактная информация'), version=2
        ),
    )


async def show_bot_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает информацию о боте."""
    query = update.callback_query
    await query.answer()

    async with ClientSession() as session:
        async with session.get(f'{API_URL}/botinfo') as response:
            if response.status == 200:
                data = await response.json()
            else:
                data = {
                    'bot_info': 'Информация временно недоступна',
                    'about_company': 'Информация временно недоступна',
                    'contacts': 'Информация временно недоступна',
                }

    # Создаем клавиатуру с кнопкой возврата
    keyboard = [
        [InlineKeyboardButton('🔙 В главное меню', callback_data='back')]
    ]

    await query.edit_message_text(
        text=build_bot_info_card(data),
        parse_mode='MarkdownV2',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
