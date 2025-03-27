from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
)
import aiohttp

# Конфигурация
API_BASE_URL = "http://127.0.0.1:8000"
FAVORITES_STATE = 1


def get_product_keyboard(product_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📖 Подробнее",
                callback_data=f"details_{product_id}"
            ),
            InlineKeyboardButton(
                "🛒 В корзину",
                callback_data=f"cart_{product_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "❌ Удалить",
                callback_data=f"remove_{product_id}"
            ),
        ]
    ])


async def fetch_favorites(telegram_id: int):
    url = f"{API_BASE_URL}/favorites/me"
    payload = {"telegram_id": telegram_id}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            print(f"Connection error: {str(e)}")
            return []


async def show_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    try:
        if update.message:
            await update.message.delete()
        favorites = await fetch_favorites(telegram_id)
        if not favorites:
            await update.callback_query.edit_message_text("🌟 Ваш список пуст.")
            return ConversationHandler.END
        print(favorites)
        for firework in favorites:
            await context.bot.send_message(
                chat_id=telegram_id,
                text=f"{firework['firework']['name']}\n",
                reply_markup=get_product_keyboard(firework['firework']['id'])
            )
        return FAVORITES_STATE

    except Exception:
        await update.callback_query.edit_message_text("⚠️ Ошибка.")
        return ConversationHandler.END


async def handle_favorites_actions(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    telegram_id = query.from_user.id
    if '_' in data:
        firework_id = int(data.split("_")[1])

        try:
            if data.startswith("details_"):
                url = f"{API_BASE_URL}/fireworks/{firework_id}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        headers={"Accept": "application/json"}
                    ) as response:
                        if response.status == 200:
                            firework = await response.json()

                await query.edit_message_text(
                    f"📦 <b>{firework['name']}</b>\n"
                    f"💵 Цена: {firework['price']} ₽\n"
                    f"📝 Описание: {firework['description']}",
                    parse_mode="HTML",
                    reply_markup=get_product_keyboard(firework_id)
                )

            elif data.startswith("cart_"):
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.post(
                            f"{API_BASE_URL}/user/cart",
                            json={
                                "telegram_id": telegram_id,
                                "firework_id": firework_id
                            }
                        ) as response:
                            if response.status == 201:
                                await query.answer("Товар добавлен в корзину 🛒")
                            else:
                                error = await response.text()
                                print(f"Error: {error}")
                                await query.answer("⚠️ Ошибка!")
                    except aiohttp.ClientError:
                        await query.answer("🚫 Ошибка соединения с сервером")

            elif data.startswith("remove_"):
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.delete(
                            f"{API_BASE_URL}/favorites/{firework_id}",
                            json={
                                "telegram_id": telegram_id
                            }
                        ) as response:
                            if response.status == 200:
                                await query.edit_message_text("❌ Товар убран")
                            else:
                                error = await response.text()
                                print(f"Delete error: {error}")
                                await query.answer("⚠️ Не удалось удалить!")
                    except aiohttp.ClientError:
                        await query.answer("🚫 Ошибка соединения с сервером")
        except Exception as e:
            await query.answer(f"⚠️ Произошла ошибка: {str(e)}")

    return FAVORITES_STATE


def setup_favorites_handler(application):
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(show_favorites, pattern="^favorites$")],
        states={
            FAVORITES_STATE: [CallbackQueryHandler(handle_favorites_actions)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
