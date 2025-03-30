import httpx
from telegram import CallbackQuery, InlineKeyboardMarkup, Update
from telegram.helpers import escape_markdown

from src.bot.keyboards import keyboard_main

# Предположил, что главное меню определено в main.py

API_BASE_URL = 'http://localhost:8000/api/v1'  # Уточнить у команды


async def get_user_id_from_telegram(update: Update) -> str | None:
    """Получение user_id по telegram_id."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'{API_BASE_URL}/users/get-id',
            json={'telegram_id': update.effective_user.id},
        )
        if response.status_code == 200:
            return response.json()['user_id']
        return None


async def return_to_main(query: CallbackQuery) -> None:
    """Унифицированный возврат в главное меню."""
    await query.answer()
    await query.edit_message_text(
        'Выберите пункт меню:',
        reply_markup=InlineKeyboardMarkup(keyboard_main),
    )
    return


MARCDOWN_VERSION = 2


def croling_content(content: str) -> str:
    return escape_markdown(content, version=MARCDOWN_VERSION)


# В будущем может быть ConversationHandler.END
