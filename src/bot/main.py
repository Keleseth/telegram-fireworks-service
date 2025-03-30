import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.bot import config
from src.bot.handlers.cart import (
    change_quantity,
    checkout,
    clear_cart_handler,
    handle_new_quantity,
    remove_item,
    view_cart,
)

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


async def menu(update: Update, context: CallbackContext):
    reply_markup = InlineKeyboardMarkup(keyboard_main)
    await update.message.reply_text(
        'Выберите пункт меню:', reply_markup=reply_markup
    )


async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    option = query.data

    if option == 'back':
        reply_markup = InlineKeyboardMarkup(keyboard_main)
        await query.edit_message_text(
            text='Выберите пункт меню:', reply_markup=reply_markup
        )
    elif option == 'cart':
        await view_cart(update, context)
    elif option == 'checkout':  # Обработка кнопки "Оформить заказ"
        await checkout(update, context)
    elif option.startswith(
        'change_item_'
    ):  # Обработка кнопки изменения количества
        item_id = option.split('_')[2]
        await change_quantity(
            update, context, item_id
        )  # Запрашиваем новое количество
    elif option.startswith('remove_'):
        item_id = option.split('_')[1]
        await remove_item(
            update, context, item_id
        )  # Запрашиваем новое количество
    elif option == 'clear_cart':  # Обработка кнопки "Оформить заказ"
        await clear_cart_handler(update, context)
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

    checkout_handler = CallbackQueryHandler(checkout, pattern='^checkout$')
    application.add_handler(checkout_handler)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_quantity)
    )
    application.add_handler(
        CallbackQueryHandler(remove_item, pattern='^remove_')
    )
    application.add_handler(
        CallbackQueryHandler(clear_cart_handler, pattern='clear_cart')
    )

    application.run_polling()
