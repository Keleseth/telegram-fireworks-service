import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
)

from src.bot.bot_messages import build_firework_card
from src.bot.utils import show_media
from src.schemas.cart import UserIdentificationSchema

# Конфигурация
API_BASE_URL = 'http://127.0.0.1:8000'
FAVORITES_STATE = 1


def get_product_keyboard(product_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                '📖 Подробнее', callback_data=f'details_{product_id}'
            ),
            InlineKeyboardButton(
                '🛒 В корзину', callback_data=f'cart_{product_id}'
            ),
        ],
        [
            InlineKeyboardButton(
                '❌ Удалить', callback_data=f'remove_{product_id}'
            ),
        ],
    ])


cancel_favorite_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton('📖 В главное меню', callback_data='back')],
    [InlineKeyboardButton('📖 Смотреть избранное', callback_data='favorites')],
])


def get_navigation_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('В главное меню', callback_data='back')]
    ])


async def fetch_favorites(telegram_id: int):
    url = f'{API_BASE_URL}/favorites/me'
    payload = {'telegram_id': telegram_id}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                url, json=payload, headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except aiohttp.ClientError as e:
            print(f'Connection error: {str(e)}')
            return []


async def show_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id
    try:
        favorites = await fetch_favorites(telegram_id)
        if not favorites:
            await query.edit_message_text('🌟 Ваш список пуст.')
            return ConversationHandler.END
        fireworks = [favorite['firework'] for favorite in favorites]
        for firework in fireworks:
            #if firework.get('media'):
                #await show_media(query, context, firework['media'])
            await query.message.reply_text(
                text=build_firework_card(firework, full_info=False),
                reply_markup=get_product_keyboard(firework['id']),
                parse_mode='MarkdownV2',
            )
        await query.message.reply_text(
            text='🌟 Навигация',
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        'Назад', callback_data='cancel_favorite'
                    )
                ]
            ]),
            parse_mode='MarkdownV2',
        )
        return FAVORITES_STATE

    except Exception:
        await query.edit_message_text('⚠️ Ошибка.')
        return ConversationHandler.END


async def handle_favorites_actions(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    data = query.data
    telegram_id = update.effective_user.id
    if '_' in data:
        firework_id = int(data.split('_')[-1])

        try:
            if data.startswith('details_'):
                url = f'{API_BASE_URL}/fireworks/{firework_id}'
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url, headers={'Accept': 'application/json'}
                    ) as response:
                        if response.status == 200:
                            firework = await response.json()
                        await query.edit_message_text(
                            build_firework_card(firework),
                            parse_mode='MarkdownV2',
                            reply_markup=get_product_keyboard(firework_id),
                        )

            elif data.startswith('cart_'):
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.post(
                            f'{API_BASE_URL}/user/cart',
                            json=dict(
                                create_data=dict(
                                    amount=1, firework_id=firework_id
                                ),
                                user_ident=UserIdentificationSchema(
                                    telegram_id=telegram_id
                                ).model_dump(),
                            ),
                        ) as response:
                            print(999, response.status)
                            if response.status == 201:
                                await query.edit_message_text(
                                    'Товар добавлен в корзину 🛒'
                                )
                            else:
                                error = await response.text()
                                print(f'Error: {error}')
                                await query.answer('⚠️ Ошибка!')
                    except aiohttp.ClientError:
                        await query.answer('🚫 Ошибка соединения с сервером')

            elif data.startswith('remove_'):
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.delete(
                            f'{API_BASE_URL}/favorites/{firework_id}',
                            json={'telegram_id': telegram_id},
                        ) as response:
                            if response.status == 200:
                                await query.edit_message_text('❌ Товар убран')
                            else:
                                error = await response.text()
                                print(f'Delete error: {error}')
                                await query.answer('⚠️ Не удалось удалить!')
                    except aiohttp.ClientError:
                        await query.answer('🚫 Ошибка соединения с сервером')
            return FAVORITES_STATE
        except Exception as e:
            await query.answer(f'⚠️ Произошла ошибка: {str(e)}')
            return FAVORITES_STATE
    return FAVORITES_STATE


async def cancel_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        'Навигация', reply_markup=cancel_favorite_keyboard
    )
    return ConversationHandler.END


def setup_favorites_handler(application: ApplicationBuilder):
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(show_favorites, pattern='^favorites$')
        ],
        states={
            FAVORITES_STATE: [
                CallbackQueryHandler(
                    handle_favorites_actions, pattern='^(details|cart|remove)_'
                )
            ],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_favorite, pattern='^cancel_favorite$')
        ],
    )
    application.add_handler(conv_handler)
