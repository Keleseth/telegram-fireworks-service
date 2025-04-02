import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

API_BASE_URL = 'http://nginx:8000'

CHANGE_QUANTITY = 1


async def send_request(method: str, url: str, data: dict = None) -> dict:
    """Универсальная функция для отправки запросов на сервер."""
    async with aiohttp.ClientSession() as session:
        async with getattr(session, method)(url, json=data) as response:
            if response.status == 200:
                return await response.json()
            error_message = await response.text()
            print(f'Error Message: {error_message}')
            return {'error': error_message}


async def add_to_cart(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Добавляет товар в корзину через API."""
    query = update.callback_query
    await query.answer()

    product_id = query.data.split('_')[-1]
    user_id = str(update.effective_user.id)

    data = await send_request(
        'post',
        f'{API_BASE_URL}/user/cart',
        {
            'firework_id': int(product_id),
            'quantity': 1,
            'telegram_id': user_id,
        },
    )

    await query.message.reply_text(
        data.get('message', 'Ошибка при добавлении в корзину')
    )


async def checkout(update: Update, context: CallbackContext) -> None:
    """Обрабатывает кнопку оформления заказа."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)

    cart_messages = context.user_data.get('cart_messages', [])
    if cart_messages:
        for message_id in cart_messages:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id, message_id=message_id
                )
                print(f'Удалено сообщение с ID: {message_id}')
            except Exception as e:
                print(f'Не удалось удалить сообщение с ID {message_id}: {e}')

        context.user_data['cart_messages'] = []

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

    data = await send_request(
        'post', f'{API_BASE_URL}/user/cart/me', {'telegram_id': user_id}
    )

    if 'error' in data:
        print(f'Ошибка при получении корзины, статус: {data["error"]}')
        await message.reply_text(
            f'❌ Ошибка при получении данных корзины: {data["error"]}'
        )
        return

    if isinstance(data, list):
        cart_items = data
    elif isinstance(data, dict):
        cart_items = data.get('items', [])
    else:
        cart_items = []

    if not cart_items:
        await message.reply_text('Ваша корзина пуста.')
        return

    context.user_data['cart_items'] = cart_items
    context.user_data['cart_messages'] = []

    if update.callback_query:
        if 'cart_message' in context.user_data:
            cart_message = context.user_data['cart_message']
            try:
                await cart_message.edit_text(
                    '🛒 *Ваша корзина:*\n', parse_mode='Markdown'
                )
            except Exception as e:
                print(f'Ошибка при редактировании сообщения: {e}')
                cart_message = await message.reply_text(
                    '🛒 *Ваша корзина:*\n', parse_mode='Markdown'
                )
                context.user_data['cart_messages'].append(
                    cart_message.message_id
                )
        else:
            cart_message = await message.reply_text(
                '🛒 *Ваша корзина:*\n', parse_mode='Markdown'
            )
            context.user_data['cart_messages'].append(cart_message.message_id)
    else:
        cart_message = await message.reply_text(
            '🛒 *Ваша корзина:*\n', parse_mode='Markdown'
        )
        context.user_data['cart_messages'].append(cart_message.message_id)

    total_price = 0
    buttons = []
    for item in cart_items:
        firework_id = item['firework']['id']
        product_name = item['firework']['name']
        amount = item['amount']
        price = float(item['firework']['price']) * amount
        cost = float(item['firework']['price'])
        total_price += price

        cart_text = (
            f'🔹 *{product_name}*: {amount} шт. '
            f'Цена за шт.: {cost:.0f}. Стоимость - {price:.0f}'
        )

        buttons = [
            [
                InlineKeyboardButton(
                    '✏ Изменить количество',
                    callback_data=f'change_item_{str(firework_id)}',
                )
            ],
            [
                InlineKeyboardButton(
                    '❌ Удалить', callback_data=f'remove_{str(firework_id)}'
                )
            ],
        ]

        message = await message.reply_text(
            cart_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='Markdown',
        )
        context.user_data['cart_messages'].append(message.message_id)

    checkout_buttons = [
        [
            InlineKeyboardButton(
                '❌ Очистить корзину', callback_data='clear_cart'
            )
        ],
        [InlineKeyboardButton('✅ Оформить заказ', callback_data='checkout')],
    ]
    total_price_message = await message.reply_text(
        f'Итоговая стоимость корзины: {total_price:.0f}',
        reply_markup=InlineKeyboardMarkup(checkout_buttons),
        parse_mode='Markdown',
    )
    context.user_data['cart_messages'].append(total_price_message.message_id)


async def remove_item(
    update: Update, context: CallbackContext, item_id: str
) -> None:
    """Обрабатывает кнопку удаления товара из корзины."""
    query = update.callback_query
    await query.answer()
    print(item_id)
    user_id = str(update.effective_user.id)

    cart_items = context.user_data.get('cart_items', [])
    product_name = next(
        (
            item['firework']['name']
            for item in cart_items
            if str(item['firework']['id']) == item_id
        ),
        None,
    )

    if not product_name:
        await update.callback_query.message.reply_text(
            'Ошибка: Товар не найден.'
        )
        return

    cart_messages = context.user_data.get('cart_messages', [])
    if cart_messages:
        for message_id in cart_messages:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id, message_id=message_id
                )
                print(f'Удалено сообщение с ID: {message_id}')
            except Exception as e:
                print(f'Не удалось удалить сообщение с ID {message_id}: {e}')

        context.user_data['cart_messages'] = []

    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f'{API_BASE_URL}/user/cart/{item_id}',
            json={'telegram_id': user_id},
        ) as response:
            print(item_id)
            if response.status == 200:
                await query.message.reply_text(
                    f'✅ Товар {product_name} успешно удален из корзины.'
                )
            else:
                error_message = await response.text()
                await query.message.reply_text(f'❌ Ошибка: {error_message}')

    await view_cart(update, context)


async def clear_cart_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)

    cart_messages = context.user_data.get('cart_messages', [])
    if cart_messages:
        for message_id in cart_messages:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id, message_id=message_id
                )
                print(f'Удалено сообщение с ID: {message_id}')
            except Exception as e:
                print(f'Не удалось удалить сообщение с ID {message_id}: {e}')

        context.user_data['cart_messages'] = []

    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f'{API_BASE_URL}/user/cart/',
            json={'telegram_id': user_id},
        ) as response:
            if response.status == 200:
                await query.message.reply_text('✅ Корзина успешно очищена!')
            else:
                error_message = await response.text()
                await query.message.reply_text(f'❌ Ошибка: {error_message}')

    await view_cart(update, context)


async def change_quantity_entry(
    update: Update, context: CallbackContext
) -> int:
    """Шаг 1: Срабатывает при нажатии на кнопку 'change_item_{item_id}'.

    Извлекаем item_id, сохраняем и спрашиваем новое кол-во.
    """
    query = update.callback_query
    print(query)
    await query.answer()

    # Получаем item_id из callback_data: "change_item_123"
    data = query.data  # например, "change_item_123"
    parts = data.split('_')  # ["change", "item", "123"]
    print(parts)
    if len(parts) < 3:
        await query.message.reply_text('Некорректный callback_data!')
        return ConversationHandler.END

    item_id = parts[2]
    context.user_data['current_item_id'] = item_id

    await query.message.reply_text(
        'Введите новое количество для этого товара:'
    )
    print('--------------------------------------------------')
    print('Вход в конверс 1')
    # Переходим в состояние ожидания текста (CHANGE_QUANTITY)
    return CHANGE_QUANTITY


async def handle_new_quantity(update: Update, context: CallbackContext) -> int:
    """Шаг 2: Получаем новое число от пользователя и обновляем количество."""
    print('--------------------------------------------------')
    print('Вход в конверс 2')
    new_amount_text = update.message.text.strip()

    if not new_amount_text.isdigit() or int(new_amount_text) <= 0:
        await update.message.reply_text(
            'Пожалуйста, введите целое число больше нуля.'
        )
        return CHANGE_QUANTITY

    new_amount = int(new_amount_text)

    item_id = context.user_data.get('current_item_id')

    if item_id is None:
        await update.message.reply_text(
            'Ошибка! Не найден товар для изменения количества.'
        )
        return ConversationHandler.END

    cart_items = context.user_data.get('cart_items', [])
    product_name = next(
        (
            item['firework']['name']
            for item in cart_items
            if str(item['id']) == item_id
        ),
        None,
    )

    user_id = str(update.effective_user.id)
    print(item_id)
    async with aiohttp.ClientSession() as session:
        async with session.patch(
            f'{API_BASE_URL}/user/cart/{item_id}',
            json={
                'update_data': {'telegram_id': user_id, 'amount': new_amount},
                'user_ident': {'telegram_id': user_id},
            },
        ) as response:
            print(response)
            name_text = f' {product_name}' if product_name else ''
            await update.message.reply_text(
                f'Количество товара{name_text} обновлено на {new_amount} шт.'
            )

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
                )
            ],
        },
        fallbacks=[],
    )
    application.add_handler(cart_conv_handler)
