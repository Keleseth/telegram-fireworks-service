from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from src.bot.states import SELECT_MENU_POSITION

keyboard_main = [
    [InlineKeyboardButton('Каталог продуктов', callback_data='catalog')],
    [InlineKeyboardButton('Акции и скидки', callback_data='promotions')],
    [InlineKeyboardButton(
        'Подобрать товар по параметрам',
        callback_data='product_filter'
    )],
    [InlineKeyboardButton('Поиск товаров', callback_data='search')],
    [InlineKeyboardButton('Избранные товары', callback_data='favorites')],
    [InlineKeyboardButton('Посмотреть корзину', callback_data='cart')],
    [InlineKeyboardButton('Оформить заказ', callback_data='checkout')],
    [InlineKeyboardButton('История заказов', callback_data='orders')],
    [InlineKeyboardButton('Информация о боте', callback_data='bot_info')],
]

keyboard_back = [
    [InlineKeyboardButton('Назад', callback_data='back')]
]


async def menu(update: Update, context: CallbackContext):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            text='Вы выбрали каталог',
            reply_markup=InlineKeyboardMarkup(keyboard_main)
        )
    else:
        await update.message.reply_text(
            text='Вы выбрали каталог',
            reply_markup=InlineKeyboardMarkup(keyboard_main)
        )
    return SELECT_MENU_POSITION
