import logging
from enum import Enum

import aiohttp
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.bot.handlers.users import TelegramUserManager

logging.basicConfig(level=logging.INFO)

API_BASE_URL = 'http://nginx:8000'


class CartState(Enum):
    CHANGE_QUANTITY = 1


CHANGE_QUANTITY = 1


async def send_request(method: str, url: str, data: dict = None) -> dict:
    """Универсальная функция для отправки запросов на сервер."""
    method = method.lower()
    try:
        async with aiohttp.ClientSession() as session:
            async with getattr(session, method)(url, json=data) as response:
                if response.ok:
                    return await response.json()
                error_message = await response.text()
                logging.error(f'Ошибка запроса: {error_message}')
                return {'error': error_message}
    except Exception as e:
        logging.error(f'Ошибка соединения: {e}')
        return {'error': 'Ошибка соединения с сервером'}


async def checkout(update: Update, context: CallbackContext) -> None:
    """Обрабатывает кнопку оформления заказа."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    await delete_cart_messages(update, context)

    data = await send_request(
        'post', f'{API_BASE_URL}/orders', {'telegram_id': user_id}
    )

    if 'error' not in data:
        await query.message.reply_text(
            '✅ Ваш заказ успешно оформлен! Спасибо за покупку.'
        )
    else:
        await query.message.reply_text(
            '❌ Произошла ошибка при оформлении заказа.'
            'Пожалуйста, попробуйте снова.'
        )


async def view_cart(update: Update, context: CallbackContext) -> None:
    message = (
        update.message if update.message else update.callback_query.message
    )
    user_id = str(update.effective_user.id)
    await delete_cart_messages(update, context)
    data = await send_request(
        'post', f'{API_BASE_URL}/user/cart/me', {'telegram_id': user_id}
    )
    if 'error' in data:
        await message.reply_text(
            f'❌ Ошибка при получении данных корзины: {data["error"]}'
        )
        return

    cart_items = data if isinstance(data, list) else data.get('items', [])
    if not cart_items:
        await message.reply_text('Ваша корзина пуста.')
        return

    context.user_data['cart_items'] = cart_items
    context.user_data['cart_messages'] = []

    total_price = 0
    buttons = []

    message_start = await message.reply_text(
        '🛒 Ваша корзина:',
        parse_mode='Markdown',
    )
    context.user_data['cart_messages'].append(message_start.message_id)

    for item in cart_items:
        firework_id = item['firework']['id']
        product_name = item['firework']['name']
        amount = item['amount']
        price = float(item['firework']['price'])
        total_price += price * amount

        cart_text = (
            f'🔹 *{product_name}*: *{amount}* шт.\n'
            f'Цена за шт.: *{price:.2f}* руб.'
        )
        buttons = [
            [
                InlineKeyboardButton(
                    '✏ Изменить количество',
                    callback_data=f'change_item_{firework_id}',
                )
            ],
            [
                InlineKeyboardButton(
                    '❌ Удалить из корзины',
                    callback_data=f'remove_{firework_id}',
                )
            ],
        ]
        message = await message.reply_text(
            cart_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='Markdown',
        )
        context.user_data['cart_messages'].append(message.message_id)

    total_message = f'Итоговая стоимость корзины: *{total_price:.2f}* руб.'
    checkout_buttons = [
        [
            InlineKeyboardButton(
                '❌ Очистить корзину', callback_data='clear_cart'
            )
        ],
        [InlineKeyboardButton('✅ Оформить заказ', callback_data='checkout')],
        [InlineKeyboardButton('🏠 В главное меню', callback_data='back')],
    ]
    cart_message = await message.reply_text(
        total_message,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(checkout_buttons),
    )
    context.user_data['cart_messages'].append(cart_message.message_id)


async def remove_item(
    update: Update, context: CallbackContext, item_id: str
) -> None:
    """Обрабатывает кнопку удаления товара из корзины."""
    query = update.callback_query
    await query.answer()
    user_id = str(update.effective_user.id)

    product_name = get_product_name(context, item_id)
    await delete_cart_messages(update, context)

    await send_request(
        'delete',
        f'{API_BASE_URL}/user/cart/{item_id}',
        {'telegram_id': user_id},
    )
    await query.message.reply_text(
        f'✅ Товар {product_name} успешно удален из корзины.'
    )
    await view_cart(update, context)


async def clear_cart_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    await delete_cart_messages(update, context)

    await send_request(
        'delete', f'{API_BASE_URL}/user/cart/', {'telegram_id': user_id}
    )
    await query.message.reply_text('✅ Корзина успешно очищена!')
    await view_cart(update, context)


async def change_quantity_entry(
    update: Update, context: CallbackContext
) -> int:
    """Шаг 1: Срабатывает при нажатии на кнопку 'change_item_{item_id}'.

    Извлекаем item_id, сохраняем и спрашиваем новое кол-во.
    """
    query = update.callback_query
    await query.answer()

    item_id = query.data.split('_')[-1]
    context.user_data['current_item_id'] = item_id
    product_name = get_product_name(context, item_id)
    await delete_cart_messages(update, context)
    back_button = InlineKeyboardButton('🔙 Назад', callback_data='main-menu')
    reply_markup = InlineKeyboardMarkup([[back_button]])

    message_1 = await query.message.reply_text(
        f'Введите новое количество для товара *{product_name}*, '
        f'или нажмите "Назад" для отмены.',
        parse_mode='Markdown',
        reply_markup=reply_markup,
    )
    message_2 = await query.message.reply_text(
        'Чтобы прервать выполнение, нажмите Назад',
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data['cart_messages'].append(message_1.message_id)
    context.user_data['cart_messages'].append(message_2.message_id)
    return CartState.CHANGE_QUANTITY.value


async def handle_new_quantity(update: Update, context: CallbackContext) -> int:
    """Шаг 2: Получаем новое число от пользователя и обновляем количество."""
    new_amount_text = update.message.text.strip()

    if not new_amount_text.isdigit() or int(new_amount_text) <= 0:
        await update.message.reply_text(
            'Пожалуйста, введите целое число больше нуля.'
        )
        return CartState.CHANGE_QUANTITY.value

    new_amount = int(new_amount_text)
    item_id = context.user_data.get('current_item_id')

    if item_id is None:
        await update.message.reply_text('Ошибка: товар не найден.')
        return ConversationHandler.END

    product_name = get_product_name(context, item_id)
    user_id = str(update.effective_user.id)
    await send_request(
        'patch',
        f'{API_BASE_URL}/user/cart/{item_id}',
        {
            'update_data': {'telegram_id': user_id, 'amount': new_amount},
            'user_ident': {'telegram_id': user_id},
        },
    )
    await update.message.reply_text(
        f'✅ Количество товара *{product_name}* '
        f'обновлено на *{new_amount}* шт.',
        parse_mode='Markdown',
    )
    user_manager = TelegramUserManager(application=context.application)
    keyboard = user_manager.main_keyboard()

    await update.message.reply_text(
        text='Ваша корзина обновлена', reply_markup=keyboard
    )
    await view_cart(update, context)
    return ConversationHandler.END


async def handle_back_to_cart(update: Update, context: CallbackContext) -> int:
    """Универсальный выход из любого ConversationHandler."""
    query = update.callback_query
    await query.answer()
    user_manager = TelegramUserManager(application=context.application)
    keyboard = user_manager.main_keyboard()
    message = (
        update.message if update.message else update.callback_query.message
    )
    await message.reply_text(text='Изменения отменены', reply_markup=keyboard)
    await view_cart(update, context)
    return ConversationHandler.END


def setup_cart_handler(application: ApplicationBuilder) -> None:
    cart_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                change_quantity_entry, pattern=r'^change_item_\d+$'
            )
        ],
        states={
            CHANGE_QUANTITY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, handle_new_quantity
                ),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(handle_back_to_cart, pattern='^main-menu$')
        ],
    )
    application.add_handler(cart_conv_handler)


async def delete_cart_messages(
    update: Update, context: CallbackContext
) -> None:
    """Удаляет все сообщения, связанные с корзиной, из чата."""
    cart_messages = context.user_data.get('cart_messages', [])
    if not cart_messages:
        return

    for message_id in cart_messages:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id, message_id=message_id
            )
            print(f'Удалено сообщение с ID: {message_id}')
        except Exception as e:
            print(f'Не удалось удалить сообщение с ID {message_id}: {e}')

    context.user_data['cart_messages'] = []


def get_product_name(context: CallbackContext, item_id: str) -> str:
    """Ищет название товара по его ID в корзине пользователя."""
    cart_items = context.user_data.get('cart_items', [])
    return next(
        (
            item['firework']['name']
            for item in cart_items
            if str(item['firework']['id']) == item_id
        ),
        'Неизвестный товар',
    )
