import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from src.bot import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            'Добро пожаловать в телеграм бот Joker Fireworks! '
            'Для входа в меню введите /menu'
        ),
    )


keyboard_main = [
    [InlineKeyboardButton('Каталог продуктов', callback_data='catalog')],
    [InlineKeyboardButton('Акции и скидки', callback_data='promotions')],
    [
        InlineKeyboardButton(
            'Подобрать товар по параметрам', callback_data='product_filter'
        )
    ],
    [InlineKeyboardButton('Поиск товаров', callback_data='search')],
    [InlineKeyboardButton('Избранные товары', callback_data='favorites')],
    [InlineKeyboardButton('Посмотреть корзину', callback_data='cart')],
    [InlineKeyboardButton('Оформить заказ', callback_data='checkout')],
    [InlineKeyboardButton('История заказов', callback_data='orders')],
    [InlineKeyboardButton('Информация о боте', callback_data='bot_info')],
]

keyboard_back = [[InlineKeyboardButton('Назад', callback_data='back')]]


async def menu(update: Update, contex: CallbackContext):
    reply_markup = InlineKeyboardMarkup(keyboard_main)
    await update.message.reply_text(
        'Выберите пункт меню:', reply_markup=reply_markup
    )


async def button(update: Update, contex: CallbackContext):
    query = update.callback_query
    await query.answer()
    option = query.data

    if option == 'back':
        reply_markup = InlineKeyboardMarkup(keyboard_main)
        await query.edit_message_text(
            text='Выберите пункт меню:', reply_markup=reply_markup
        )
    else:
        reply_markup = InlineKeyboardMarkup(keyboard_back)
        await query.edit_message_text(
            text=f'Выбран пункт: {option}', reply_markup=reply_markup
        )


if __name__ == '__main__':
    application = ApplicationBuilder().token(config.TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    menu_handler = CommandHandler('menu', menu)
    application.add_handler(menu_handler)

    button_handler = CallbackQueryHandler(button)
    application.add_handler(button_handler)

    application.run_polling()
