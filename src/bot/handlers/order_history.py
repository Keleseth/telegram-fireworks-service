import logging

from aiohttp import ClientSession
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Предполагаем, что эти утилиты работают как надо
from src.bot.utils import API_BASE_URL

logger = logging.getLogger(__name__)

# Состояния
AWAITING_ORDER_DETAILS, AWAITING_NEW_ADDRESS = range(2)

# Ключи context.user_data
DIALOG_DATA = 'dialog_data'
# Кэш адресов теперь будет частью DIALOG_DATA
# ADDRESS_CACHE = 'address_cache'

# Кнопки
BACK_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton('Назад', callback_data='back')]
])
# Используем CANCEL_KEEP_KEYBOARD для отмены повторного заказа,
# где пользователь НЕ выбрал адрес (заказ остается без адреса)
CANCEL_REPEAT_NO_ADDRESS_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            'Отмена (оставить без адреса)', callback_data='repeat_cancel_addr'
        )
    ]
])
# Кнопка Отмены для ввода нового адреса (возврат к выбору адреса)
CANCEL_NEW_ADDRESS_INPUT_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton('Отмена', callback_data='cancel_new_addr_input')]
])

# Сообщения
ORDER_HISTORY_MESSAGE = 'История ваших заказов:\n\n{history_text}'
# Используем ТЕКСТ адреса
ORDER_DETAILS_MESSAGE = (
    'Заказ #{order_id} ({status}):\n'
    'Состав:\n{order_summary}\n'
    'Итого: {total} руб.\n'
    'Адрес: {address}\n'
    'ФИО: {fio}\n'
    'Телефон: {phone}\n'
    'Звонок оператора: {operator_call}\n'
)
ORDER_REPEAT_MESSAGE = (
    'Заказ #{order_id} успешно повторён!\n'
    'Состав:\n{order_summary}\n'
    'Итого: {total} руб.\n'
    'Адрес: {address}'  # <--- ТЕКСТ АДРЕСА
)
PLACE_ORDER_ADDRESS_PROMPT = (
    '📍 Введите адрес доставки\n💬 Пример: г. Москва ул. Ленина, д. 1'
)
ORDER_ADDRESS_PROMPT = (
    '📍 Введите новый адрес доставки\n💬 Пример: г. Москва ул. Ленина, д. 1'
)
ORDER_ADDRESS_UPDATED_MESSAGE = '✅ Адрес доставки успешно обновлён!'
CHOOSE_ADDRESS_PROMPT = (
    '🏠 Выберите адрес доставки из сохраненных или введите новый:'
)
ADDRESS_SAVED_MESSAGE = (
    '✅ Адрес доставки успешно обновлён!\nНовый адрес: {address}'
)
REPEAT_CHOOSE_ADDRESS_PROMPT = (
    '👍 Заказ #{order_id_to_repeat} повторен (новый ID: {new_order_id}).\n'
    'Теперь выберите адрес доставки для нового заказа:'
)
REPEAT_ORDER_CONFIRMED_MESSAGE = (
    '✅ Повторный заказ #{order_id} оформлен!\nАдрес: {address}'
)
REPEAT_ORDER_CANCELLED_NO_ADDRESS_MESSAGE = (
    '✅ Заказ #{order_id} создан (повтор заказа).\n'
    '{order_summary}\nИтого: {total} руб.\n'
    'Адрес не указан. Вы можете изменить его позже.'
)
ERROR_FETCHING_ORDERS = '😿 Ошибка при загрузке истории заказов.'
ERROR_FETCHING_ADDRESSES = '😿 Ошибка при загрузке ваших сохраненных адресов.'
ERROR_ORDER_NOT_FOUND_LOCAL = (
    '😿 Заказ не найден в локальных данных. Попробуйте обновить историю.'
)
ERROR_ORDER_NOT_FOUND_API = '😿 Ошибка при получении статуса заказа.'
ERROR_DELIVERY_STATUS = '😿 Ошибка при запросе статуса доставки. Код: {status}'
ERROR_ADDRESS_UPDATE = '😿 Ошибка при обновлении адреса заказа.'
ERROR_ADDRESS_SAVE = '😿 Ошибка при сохранении нового адреса.'
ERROR_REPEAT_ORDER = '😿 Ошибка при повторении заказа.'
ERROR_TELEGRAM_ID_MISSING = 'Ошибка: не найден telegram_id.'
INFO_NO_ORDERS = 'У вас пока нет заказов.'
INFO_ORDER_NOT_SHIPPED = 'ℹ️ Заказ не найден или еще не отправлен.'


def get_auth_headers(telegram_id: int) -> dict:
    """Возвращает заголовки для аутентификации."""
    return {'telegram-id': str(telegram_id)}


async def order_history(update: Update, context: CallbackContext) -> int:
    """Начало диалога: загрузка заказов и адресов пользователя."""
    query = update.callback_query
    await query.answer()

    if not update.effective_user or not update.effective_user.id:
        await query.edit_message_text(ERROR_TELEGRAM_ID_MISSING)
        return ConversationHandler.END
    telegram_id = update.effective_user.id

    orders = []
    user_addresses_list = []
    user_addresses_map = {}

    async with ClientSession() as session:
        try:
            async with session.post(
                f'{API_BASE_URL}/orders/me',
                headers=get_auth_headers(telegram_id),
                json={'telegram_id': telegram_id},
            ) as response:
                if response.status != 200:
                    logger.error(
                        f'Order history fetch error {response.status}:'
                        f' {await response.text()}'
                    )
                    await query.edit_message_text(ERROR_FETCHING_ORDERS)
                    return ConversationHandler.END
                orders = await response.json()
        except Exception:
            logger.exception('Exception during order fetch:')
            await query.edit_message_text(ERROR_FETCHING_ORDERS)
            return ConversationHandler.END

        # 3. Загружаем адреса пользователя
        try:
            async with session.post(
                f'{API_BASE_URL}/useraddresses/me',
                json={'telegram_id': telegram_id},
            ) as response:
                if response.status != 200:
                    logger.error(
                        f'Failed to get user addresses for {telegram_id}: '
                        f'{response.status} {await response.text()}'
                    )
                    await context.bot.send_message(
                        chat_id=telegram_id, text=ERROR_FETCHING_ADDRESSES
                    )
                else:
                    user_addresses_list = await response.json()
                    user_addresses_map = {
                        ua['user_address_id']: ua['address']
                        for ua in user_addresses_list
                        if 'user_address_id' in ua and 'address' in ua
                    }
        except Exception:
            logger.exception('Exception during address fetch:')
            await context.bot.send_message(
                chat_id=telegram_id, text=ERROR_FETCHING_ADDRESSES
            )
            return ConversationHandler.END

        try:
            async with session.post(
                f'{API_BASE_URL}/useraddresses/me',
                json={'telegram_id': telegram_id},
            ) as response:
                if response.status != 200:
                    logger.error(
                        f'Failed to get user addresses for {telegram_id}: '
                        f'{response.status} {await response.text()}'
                    )
                    await context.bot.send_message(
                        chat_id=telegram_id, text=ERROR_FETCHING_ADDRESSES
                    )
                else:
                    user_addresses_list = await response.json()
                    user_addresses_map = {
                        ua['user_address_id']: ua['address']
                        for ua in user_addresses_list
                        if 'user_address_id' in ua and 'address' in ua
                    }
        except Exception:
            logger.exception('Exception during address fetch:')
            await context.bot.send_message(
                chat_id=telegram_id, text=ERROR_FETCHING_ADDRESSES
            )

    if not orders:
        await query.edit_message_text(INFO_NO_ORDERS)
        try:
            await query.delete_message()
        except Exception:
            pass
        return ConversationHandler.END

    context.user_data[DIALOG_DATA] = {
        'flow': 'order_history',
        'telegram_id': telegram_id,
        'orders': orders,
        'addresses_map': user_addresses_map,
        'current_order_id': None,
        'new_order_details': None,
        'address_input': None,
    }

    try:
        await query.delete_message()
    except Exception as e:
        logger.warning(f'Could not delete message: {e}')

    for order in orders:
        order_summary = '\n'.join(
            f'{item["firework"]["name"]}: {item["amount"]} шт.'
            for item in order.get('order_fireworks', [])
        )
        address_text = user_addresses_map.get(
            order.get('user_address_id'), 'Не указан'
        )

        history_text = (
            f'Заказ #{order["id"]} ({order.get("status", "N/A")})\n'
            f'Состав:\n{order_summary}\n'
            f'Адрес: {address_text}\n'
            f'Итого: {order.get("total", 0)} руб.'
        )
        keyboard = [
            [
                InlineKeyboardButton(
                    'Подробнее', callback_data=f'order_{order["id"]}'
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=history_text,
            reply_markup=reply_markup,
        )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='--- Конец истории ---',
        reply_markup=BACK_KEYBOARD,
    )

    return AWAITING_ORDER_DETAILS


async def show_order(update: Update, context: CallbackContext) -> int:
    """Показывает детальную информацию о выбранном заказе."""
    query = update.callback_query
    await query.answer()

    dialog_data = context.user_data.get(DIALOG_DATA, {})

    order_id_str = query.data.split('_')[-1]
    if not order_id_str.isdigit():
        await query.edit_message_text('Ошибка ID заказа.')
        return AWAITING_ORDER_DETAILS

    order_id = int(order_id_str)
    dialog_data['current_order_id'] = order_id

    orders = dialog_data.get('orders', [])
    order = next((o for o in orders if o.get('id') == order_id), None)

    if not order:
        await query.edit_message_text(ERROR_ORDER_NOT_FOUND_LOCAL)
        return AWAITING_ORDER_DETAILS

    address_text = dialog_data.get('addresses_map', {}).get(
        order.get('user_address_id'), 'Не указан'
    )

    order_summary = '\n'.join(
        f'{item["firework"]["name"]}: {item["amount"]} шт.'
        for item in order.get('order_fireworks', [])
    )
    keyboard = []
    order_status = order.get('status')

    if order_status not in ('Shipped', 'Delivered', 'Cancelled'):
        keyboard.append([
            InlineKeyboardButton(
                'Изменить адрес', callback_data=f'edit_addr_{order_id}'
            )
        ])
    keyboard.append([
        InlineKeyboardButton(
            'Повторить заказ', callback_data=f'repeat_{order_id}'
        )
    ])
    if order_status == 'Shipped':
        keyboard.append([
            InlineKeyboardButton(
                'Статус доставки', callback_data=f'delivery_{order_id}'
            )
        ])
    keyboard.append([
        InlineKeyboardButton('Назад к списку', callback_data='back_to_list')
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = ORDER_DETAILS_MESSAGE.format(
        order_id=order['id'],
        status=order_status or 'N/A',
        order_summary=order_summary,
        total=order.get('total', 0),
        address=address_text,
        fio=order.get('fio', 'Не указано'),
        phone=order.get('phone', 'Не указано'),
        operator_call='Да' if order.get('operator_call') else 'Нет',
    )

    await query.edit_message_text(
        message_text, reply_markup=reply_markup, parse_mode='HTML'
    )
    return AWAITING_ORDER_DETAILS


async def back_to_list(update: Update, context: CallbackContext):
    """Возврат к отображению списка заказов (перезапуск order_history)."""
    update.callback_query.data = 'orders'
    return await order_history(update, context)


async def check_delivery_status(
    update: Update, context: CallbackContext
) -> int:
    """Проверяет статус доставки заказа."""
    query = update.callback_query
    await query.answer()

    dialog_data = context.user_data.get(DIALOG_DATA, {})
    telegram_id = dialog_data.get('telegram_id')
    order_id_str = query.data.split('_')[-1]
    if not order_id_str.isdigit():
        await query.edit_message_text('Ошибка ID заказа.')
        return AWAITING_ORDER_DETAILS
    order_id = int(order_id_str)
    dialog_data['current_order_id'] = order_id

    if not telegram_id:
        await query.edit_message_text(
            ERROR_TELEGRAM_ID_MISSING, reply_markup=BACK_KEYBOARD
        )
        return AWAITING_ORDER_DETAILS

    back_to_details_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                'Назад к деталям', callback_data=f'order_{order_id}'
            )
        ]
    ])

    async with ClientSession() as session:
        async with session.get(
            f'{API_BASE_URL}/orders/{order_id}/delivery_status',
            headers=get_auth_headers(telegram_id),
        ) as response:
            if response.status == 404:
                await query.edit_message_text(
                    INFO_ORDER_NOT_SHIPPED,
                    reply_markup=back_to_details_keyboard,
                )
            elif response.status != 200:
                logger.error(
                    f'Check delivery status error {response.status} '
                    f'for order {order_id}: '
                    f'{await response.text()}'
                )
                await query.edit_message_text(
                    ERROR_DELIVERY_STATUS.format(status=response.status),
                    reply_markup=back_to_details_keyboard,
                )
            else:
                data = await response.json()
                await query.edit_message_text(
                    f'Статус доставки заказа #{order_id}: '
                    f'{data.get("delivery_status", "Нет данных")}',
                    reply_markup=back_to_details_keyboard,
                )
    return AWAITING_ORDER_DETAILS


async def edit_order_address(update: Update, context: CallbackContext) -> int:
    """Показывает кнопки выбора адреса для изменения в заказе."""
    query = update.callback_query
    await query.answer()

    dialog_data = context.user_data.get(DIALOG_DATA, {})
    telegram_id = dialog_data.get('telegram_id')
    order_id_str = query.data.split('_')[-1]
    if not order_id_str.isdigit():
        await query.edit_message_text('Ошибка ID заказа.')
        return AWAITING_ORDER_DETAILS
    order_id = int(order_id_str)
    dialog_data['current_order_id'] = order_id

    if not telegram_id:
        await query.edit_message_text(ERROR_TELEGRAM_ID_MISSING)
        return AWAITING_ORDER_DETAILS

    user_addresses_list = []
    user_addresses_map = {}
    async with ClientSession() as session:
        try:
            async with session.post(
                f'{API_BASE_URL}/useraddresses/me',
                json={'telegram_id': telegram_id},
            ) as response:
                if response.status != 200:
                    logger.error(
                        f'Edit Address: '
                        f'Failed to get user addresses for {telegram_id}: '
                        f'{response.status} {await response.text()}'
                    )
                    await query.edit_message_text(ERROR_FETCHING_ADDRESSES)
                else:
                    user_addresses_list = await response.json()
                    user_addresses_map = {
                        ua['user_address_id']: ua['address']
                        for ua in user_addresses_list
                        if 'user_address_id' in ua
                    }
                    dialog_data['addresses_map'] = user_addresses_map
        except Exception:
            logger.exception('Edit Address: Exception during address fetch:')
            await query.edit_message_text(ERROR_FETCHING_ADDRESSES)

    keyboard = []
    if user_addresses_list:
        keyboard.extend([
            [
                InlineKeyboardButton(
                    ua.get('address', f'ID: {ua.get("user_address_id")} (?)'),
                    callback_data=f'set_addr_{order_id}_{
                        ua.get("user_address_id")
                    }',
                )
            ]
            for ua in user_addresses_list
            if ua.get('user_address_id') is not None
        ])

    keyboard.append([
        InlineKeyboardButton(
            '➕ Ввести новый адрес', callback_data=f'ask_new_addr_{order_id}'
        )
    ])
    keyboard.append([
        InlineKeyboardButton(
            'Назад к деталям', callback_data=f'order_{order_id}'
        )
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        CHOOSE_ADDRESS_PROMPT, reply_markup=reply_markup
    )
    return AWAITING_NEW_ADDRESS


async def ask_new_address_input(
    update: Update, context: CallbackContext
) -> int:
    """Запрашивает ввод нового адреса текстом (при изменении)."""
    query = update.callback_query
    await query.answer()

    order_id_str = query.data.split('_')[-1]
    if not order_id_str.isdigit():
        await query.edit_message_text('Ошибка ID заказа.')
        return AWAITING_NEW_ADDRESS
    order_id = int(order_id_str)

    dialog_data = context.user_data.get(DIALOG_DATA, {})
    dialog_data['current_order_id'] = order_id

    cancel_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton('Отмена', callback_data=f'edit_addr_{order_id}')]
    ])
    await query.edit_message_text(
        ORDER_ADDRESS_PROMPT, reply_markup=cancel_keyboard
    )
    return AWAITING_NEW_ADDRESS


async def set_existing_address(
    update: Update, context: CallbackContext
) -> int:
    """Устанавливает выбранный СУЩЕСТВУЮЩИЙ адрес.

    для заказа (при изменении).
    """
    query = update.callback_query
    await query.answer('Обновляю адрес...')

    parts = query.data.split('_')
    if len(parts) != 4 or not parts[2].isdigit() or not parts[3].isdigit():
        await query.edit_message_text('Ошибка данных.')
        return AWAITING_NEW_ADDRESS

    order_id = int(parts[2])
    user_address_id = int(parts[3])

    dialog_data = context.user_data.get(DIALOG_DATA, {})
    telegram_id = dialog_data.get('telegram_id')
    dialog_data['current_order_id'] = order_id

    if not telegram_id:
        await query.edit_message_text(ERROR_TELEGRAM_ID_MISSING)
        return ConversationHandler.END

    async with ClientSession() as session:
        async with session.patch(
            f'{API_BASE_URL}/orders/{order_id}/address',
            headers=get_auth_headers(telegram_id),
            json={'user_address_id': user_address_id},
        ) as response:
            if response.status != 200:
                logger.error(
                    f'Failed to update address '
                    f'for order {order_id} to existing '
                    f'{user_address_id}: '
                    f'{response.status} {await response.text()}'
                )
                await query.edit_message_text(ERROR_ADDRESS_UPDATE)
            else:
                orders = dialog_data.get('orders', [])
                for i, order in enumerate(orders):
                    if order.get('id') == order_id:
                        orders[i]['user_address_id'] = user_address_id
                        break
                dialog_data['orders'] = orders

                address_text = dialog_data.get('addresses_map', {}).get(
                    user_address_id, f'ID: {user_address_id}'
                )
                await query.edit_message_text(
                    ADDRESS_SAVED_MESSAGE.format(address=address_text)
                )

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text='Нажмите, чтобы вернуться к деталям заказа:',
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    'Детали заказа', callback_data=f'order_{order_id}'
                )
            ]
        ]),
    )
    return AWAITING_ORDER_DETAILS


async def handle_new_address_input(
    update: Update, context: CallbackContext
) -> int:
    """Обрабатывает введенный пользователем текст.

    нового адреса (при изменении).
    """
    if not update.message or not update.message.text:
        return AWAITING_NEW_ADDRESS

    address_text = update.message.text.strip()
    chat_id = update.effective_chat.id

    dialog_data = context.user_data.get(DIALOG_DATA, {})
    telegram_id = dialog_data.get('telegram_id')
    order_id = dialog_data.get('current_order_id')

    if not telegram_id or not order_id:
        await update.message.reply_text(ERROR_TELEGRAM_ID_MISSING)
        context.user_data.pop(DIALOG_DATA, None)
        return ConversationHandler.END

    dialog_data['address_input'] = address_text
    user_address_id = None

    async with ClientSession() as session:
        try:
            async with session.post(
                f'{API_BASE_URL}/addresses',
                json={'telegram_id': telegram_id, 'address': address_text},
            ) as response:
                if response.status not in (201, 200):
                    logger.error(
                        f'Edit Order: '
                        f"Failed to save address '{address_text}' for "
                        f'{telegram_id}: '
                        f'{response.status} {await response.text()}'
                    )
                    await update.message.reply_text(
                        f'{ERROR_ADDRESS_SAVE}\nПопробуйте ввести снова или '
                        'выберите существующий адрес.',
                        reply_markup=InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton(
                                    'Выбрать существующий',
                                    callback_data=f'edit_addr_{order_id}',
                                )
                            ]
                        ]),
                    )
                    return AWAITING_NEW_ADDRESS
                address_data = await response.json()
                user_address_id = address_data.get('user_address_id')
                new_address_text = address_data.get('address')
                if not user_address_id or not new_address_text:
                    raise ValueError(
                        'user_address_id or address not in response'
                    )
                dialog_data.setdefault('addresses_map', {})[
                    user_address_id
                ] = new_address_text
                dialog_data['address_input'] = new_address_text
        except Exception as e:
            logger.exception('Edit Order: Exception during address save:')
            await update.message.reply_text(
                f'{ERROR_ADDRESS_SAVE}\nОшибка: {e}',
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            'Выбрать существующий',
                            callback_data=f'edit_addr_{order_id}',
                        )
                    ]
                ]),
            )
            return AWAITING_NEW_ADDRESS

    if user_address_id:
        async with ClientSession() as session:
            async with session.patch(
                f'{API_BASE_URL}/orders/{order_id}/address',
                headers=get_auth_headers(telegram_id),
                json={'user_address_id': user_address_id},
            ) as response:
                if response.status != 200:
                    logger.error(
                        f'Edit Order: '
                        f'Failed to update order {order_id} with NEW '
                        f'address {user_address_id}: '
                        f'{response.status} {await response.text()}'
                    )
                    await update.message.reply_text(
                        f"{ERROR_ADDRESS_UPDATE}\nАдрес '{
                            dialog_data['address_input']
                        }' "
                        f'сохранен, но не применен к заказу #{order_id}.'
                    )
                else:
                    orders = dialog_data.get('orders', [])
                    for i, order in enumerate(orders):
                        if order.get('id') == order_id:
                            orders[i]['user_address_id'] = user_address_id
                            break
                    dialog_data['orders'] = orders
                    await update.message.reply_text(
                        ADDRESS_SAVED_MESSAGE.format(
                            address=dialog_data['address_input']
                        )
                    )
                    dialog_data.pop('address_input', None)

    await context.bot.send_message(
        chat_id=chat_id,
        text='Нажмите, чтобы вернуться к деталям заказа:',
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    'Детали заказа', callback_data=f'order_{order_id}'
                )
            ]
        ]),
    )
    return AWAITING_ORDER_DETAILS


async def cancel_new_addr_input(
    update: Update, context: CallbackContext
) -> int:
    """Отмена ввода нового адреса, возврат к выбору."""
    query = update.callback_query
    await query.answer()
    dialog_data = context.user_data.get(DIALOG_DATA, {})
    order_id = dialog_data.get('current_order_id')
    if order_id:
        query.data = f'edit_addr_{order_id}'
        return await edit_order_address(update, context)
    await query.edit_message_text('Ошибка, не могу вернуться к выбору адреса.')
    return await cancel_and_cleanup(update, context)


async def repeat_order(update: Update, context: CallbackContext) -> int:
    """Запускает процесс повторения заказа и запрашивает адрес."""
    query = update.callback_query
    await query.answer('Повторяем заказ...')

    dialog_data = context.user_data.get(DIALOG_DATA, {})
    telegram_id = dialog_data.get('telegram_id')
    order_id_to_repeat_str = query.data.split('_')[-1]
    if not order_id_to_repeat_str.isdigit():
        await query.edit_message_text('Ошибка ID заказа.')
        return AWAITING_ORDER_DETAILS
    order_id_to_repeat = int(order_id_to_repeat_str)

    if not telegram_id:
        await query.edit_message_text(ERROR_TELEGRAM_ID_MISSING)
        return ConversationHandler.END

    new_order_details = None
    async with ClientSession() as session:
        try:
            async with session.post(
                f'{API_BASE_URL}/orders/{order_id_to_repeat}/repeat_direct',
                headers=get_auth_headers(telegram_id),
                json={'telegram_id': telegram_id},
            ) as response:
                if response.status != 200:
                    logger.error(
                        f'Failed to repeat order {order_id_to_repeat}: '
                        f'{response.status} {await response.text()}'
                    )
                    await query.edit_message_text(ERROR_REPEAT_ORDER)
                    return AWAITING_ORDER_DETAILS
                new_order_details = await response.json()
                if not new_order_details or 'id' not in new_order_details:
                    raise ValueError('Invalid response on repeat order')
        except Exception as e:
            logger.exception('Repeat order failed:')
            await query.edit_message_text(f'{ERROR_REPEAT_ORDER}: {e}')
            return AWAITING_ORDER_DETAILS

    new_order_id = new_order_details['id']
    dialog_data['new_order_details'] = new_order_details
    dialog_data['current_order_id'] = new_order_id
    dialog_data['is_repeating'] = True

    user_addresses_map = dialog_data.get('addresses_map', {})

    keyboard = []
    if user_addresses_map:
        keyboard.extend([
            [
                InlineKeyboardButton(
                    address_text,
                    callback_data=f'repeat_set_addr_{new_order_id}_{addr_id}',
                )
            ]
            for addr_id, address_text in user_addresses_map.items()
        ])

    keyboard.append([
        InlineKeyboardButton(
            '➕ Ввести новый адрес',
            callback_data=f'repeat_ask_new_{new_order_id}',
        )
    ])
    keyboard.append([
        InlineKeyboardButton(
            'Отмена (оставить без адреса)',
            callback_data=f'repeat_cancel_addr_{new_order_id}',
        )
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        REPEAT_CHOOSE_ADDRESS_PROMPT.format(
            order_id_to_repeat=order_id_to_repeat, new_order_id=new_order_id
        ),
        reply_markup=reply_markup,
    )
    return AWAITING_NEW_ADDRESS


async def repeat_set_existing_address(
    update: Update, context: CallbackContext
) -> int:
    """Устанавливает выбранный СУЩЕСТВУЮЩИЙ адрес для ПОВТОРЕННОГО заказа."""
    query = update.callback_query
    await query.answer('Применяю адрес к новому заказу...')

    parts = query.data.split('_')
    if len(parts) != 5 or not parts[3].isdigit() or not parts[4].isdigit():
        await query.edit_message_text('Ошибка данных.')
        return AWAITING_NEW_ADDRESS

    new_order_id = int(parts[3])
    user_address_id = int(parts[4])

    dialog_data = context.user_data.get(DIALOG_DATA, {})
    telegram_id = dialog_data.get('telegram_id')
    new_order_details = dialog_data.get('new_order_details')

    if (
        not telegram_id
        or not new_order_details
        or new_order_details.get('id') != new_order_id
    ):
        await query.edit_message_text(ERROR_TELEGRAM_ID_MISSING)
        context.user_data.pop(DIALOG_DATA, None)
        return ConversationHandler.END

    async with ClientSession() as session:
        async with session.patch(
            f'{API_BASE_URL}/orders/{new_order_id}/address',
            headers=get_auth_headers(telegram_id),
            json={'user_address_id': user_address_id},
        ) as response:
            if response.status != 200:
                logger.error(
                    f'Repeat: '
                    f'Failed to set address for order {new_order_id} to '
                    f'{user_address_id}: '
                    f'{response.status} {await response.text()}'
                )
                await query.edit_message_text(ERROR_ADDRESS_UPDATE)
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=(
                        'Не удалось применить адрес. '
                        'Попробуйте повторить заказ.'
                    ),
                )
                context.user_data.pop(DIALOG_DATA, None)
                return ConversationHandler.END
            address_text = dialog_data.get('addresses_map', {}).get(
                user_address_id, f'ID: {user_address_id}'
            )
            order_summary = '\n'.join(
                f'{item["firework"]["name"]}: {item["amount"]} шт.'
                for item in new_order_details.get('order_fireworks', [])
            )
            await query.edit_message_text(
                REPEAT_ORDER_CONFIRMED_MESSAGE.format(
                    order_id=new_order_id, address=address_text
                )
                + f'\n\nСостав:\n{order_summary}\nИтого: '
                f'{new_order_details.get("total", 0)} руб.'
            )
            context.user_data.pop(DIALOG_DATA, None)
            return ConversationHandler.END


async def repeat_ask_new_address_input(
    update: Update, context: CallbackContext
) -> int:
    """Запрашивает ввод нового адреса текстом для ПОВТОРЕННОГО заказа."""
    query = update.callback_query
    await query.answer()

    new_order_id_str = query.data.split('_')[-1]
    if not new_order_id_str.isdigit():
        await query.edit_message_text('Ошибка ID заказа.')
        return AWAITING_NEW_ADDRESS
    new_order_id = int(new_order_id_str)

    dialog_data = context.user_data.get(DIALOG_DATA, {})
    dialog_data['current_order_id'] = new_order_id
    dialog_data['is_repeating'] = True

    cancel_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                'Отмена', callback_data=f'repeat_back_to_choice_{new_order_id}'
            )
        ]
    ])
    await query.edit_message_text(
        PLACE_ORDER_ADDRESS_PROMPT, reply_markup=cancel_keyboard
    )
    return AWAITING_NEW_ADDRESS


async def repeat_back_to_choice(
    update: Update, context: CallbackContext
) -> int:
    """Возврат к выбору адреса для повторного заказа после отмены ввода."""
    query = update.callback_query
    await query.answer()

    dialog_data = context.user_data.get(DIALOG_DATA, {})
    # telegram_id = dialog_data.get('telegram_id')
    new_order_details = dialog_data.get('new_order_details')
    order_id_to_repeat = '?'

    if not new_order_details:
        await query.edit_message_text('Ошибка: нет данных нового заказа.')
        return ConversationHandler.END

    new_order_id = new_order_details['id']
    user_addresses_map = dialog_data.get('addresses_map', {})
    keyboard = []
    if user_addresses_map:
        keyboard.extend([
            [
                InlineKeyboardButton(
                    address_text,
                    callback_data=f'repeat_set_addr_{new_order_id}_{addr_id}',
                )
            ]
            for addr_id, address_text in user_addresses_map.items()
        ])
    keyboard.append([
        InlineKeyboardButton(
            '➕ Ввести новый адрес',
            callback_data=f'repeat_ask_new_{new_order_id}',
        )
    ])
    keyboard.append([
        InlineKeyboardButton(
            'Отмена (оставить без адреса)',
            callback_data=f'repeat_cancel_addr_{new_order_id}',
        )
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        REPEAT_CHOOSE_ADDRESS_PROMPT.format(
            order_id_to_repeat=order_id_to_repeat, new_order_id=new_order_id
        ),
        reply_markup=reply_markup,
    )
    return AWAITING_NEW_ADDRESS


async def repeat_handle_new_address_input(
    update: Update, context: CallbackContext
) -> int:
    """Обрабатывает введенный текст нового адреса для ПОВТОРЕННОГО заказа."""
    if not update.message or not update.message.text:
        return AWAITING_NEW_ADDRESS

    address_text = update.message.text.strip()
    # chat_id = update.effective_chat.id

    dialog_data = context.user_data.get(DIALOG_DATA, {})
    telegram_id = dialog_data.get('telegram_id')
    new_order_id = dialog_data.get('current_order_id')
    new_order_details = dialog_data.get('new_order_details')

    if (
        not telegram_id
        or not new_order_id
        or not new_order_details
        or new_order_details.get('id') != new_order_id
    ):
        await update.message.reply_text(ERROR_TELEGRAM_ID_MISSING)
        context.user_data.pop(DIALOG_DATA, None)
        return ConversationHandler.END

    dialog_data['address_input'] = address_text
    user_address_id = None

    async with ClientSession() as session:
        try:
            async with session.post(
                f'{API_BASE_URL}/addresses',
                json={'telegram_id': telegram_id, 'address': address_text},
            ) as response:
                if response.status not in (201, 200):
                    logger.error(
                        f"Repeat: Failed to save address '{address_text}' for "
                        f'{telegram_id}: '
                        f'{response.status} {await response.text()}'
                    )
                    await update.message.reply_text(
                        f'{ERROR_ADDRESS_SAVE}\nПопробуйте ввести снова.',
                        reply_markup=InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton(
                                    'Отмена',
                                    callback_data=f'repeat_back_to_choice_{
                                        new_order_id
                                    }',
                                )
                            ]
                        ]),
                    )
                    return AWAITING_NEW_ADDRESS
                address_data = await response.json()
                user_address_id = address_data.get('user_address_id')
                new_address_text = address_data.get('address')
                if not user_address_id or not new_address_text:
                    raise ValueError('Invalid address save response')
                dialog_data.setdefault('addresses_map', {})[
                    user_address_id
                ] = new_address_text
                dialog_data['address_input'] = new_address_text
        except Exception as e:
            logger.exception('Repeat: Exception during address save:')
            await update.message.reply_text(
                f'{ERROR_ADDRESS_SAVE}: {e}',
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            'Отмена',
                            callback_data=f'repeat_back_to_choice_{
                                new_order_id
                            }',
                        )
                    ]
                ]),
            )
            return AWAITING_NEW_ADDRESS

    if user_address_id:
        async with ClientSession() as session:
            async with session.patch(
                f'{API_BASE_URL}/orders/{new_order_id}/address',
                headers=get_auth_headers(telegram_id),
                json={'user_address_id': user_address_id},
            ) as response:
                if response.status != 200:
                    logger.error(
                        f'Repeat: '
                        f'Failed to update order {new_order_id} with NEW '
                        f'address {user_address_id}: '
                        f'{response.status} {await response.text()}'
                    )
                    await update.message.reply_text(
                        f"{ERROR_ADDRESS_UPDATE}\nАдрес '{
                            dialog_data['address_input']
                        }' "
                        f'сохранен, но не применен к заказу #{new_order_id}.'
                    )
                    context.user_data.pop(DIALOG_DATA, None)
                    return ConversationHandler.END
                order_summary = '\n'.join(
                    f'{item["firework"]["name"]}: {item["amount"]} шт.'
                    for item in new_order_details.get('order_fireworks', [])
                )
                await update.message.reply_text(
                    REPEAT_ORDER_CONFIRMED_MESSAGE.format(
                        order_id=new_order_id,
                        address=dialog_data['address_input'],
                    )
                    + f'\n\nСостав:\n{order_summary}\nИтого: '
                    f'{new_order_details.get("total", 0)} руб.'
                )
                context.user_data.pop(DIALOG_DATA, None)
                return ConversationHandler.END
    else:
        await update.message.reply_text(
            'Не удалось получить ID сохраненного адреса.'
        )
        context.user_data.pop(DIALOG_DATA, None)
        return ConversationHandler.END


async def repeat_cancel_address(
    update: Update, context: CallbackContext
) -> int:
    """Отмена выбора адреса для повторного заказа.

    (оставляет заказ без адреса).
    """
    query = update.callback_query
    await query.answer()

    dialog_data = context.user_data.get(DIALOG_DATA, {})
    new_order_details = dialog_data.get('new_order_details')

    if not new_order_details:
        await query.edit_message_text('Ошибка: нет данных нового заказа.')
        context.user_data.pop(DIALOG_DATA, None)
        return ConversationHandler.END

    new_order_id = new_order_details['id']
    order_summary = '\n'.join(
        f'{item["firework"]["name"]}: {item["amount"]} шт.'
        for item in new_order_details.get('order_fireworks', [])
    )
    total = new_order_details.get('total', 0)

    await query.edit_message_text(
        REPEAT_ORDER_CANCELLED_NO_ADDRESS_MESSAGE.format(
            order_id=new_order_id, order_summary=order_summary, total=total
        )
    )
    context.user_data.pop(DIALOG_DATA, None)
    return ConversationHandler.END


async def cancel_and_cleanup(update: Update, context: CallbackContext) -> int:
    """Общий обработчик отмены/назад, который чистит user_data."""
    query = update.callback_query
    await query.answer()
    try:
        await query.delete_message()
    except Exception:
        await query.edit_message_text('Действие отменено.')

    context.user_data.pop(DIALOG_DATA, None)
    logger.info('Conversation cancelled and cleaned up.')
    return ConversationHandler.END


def register_handlers(application: Application) -> None:
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(order_history, pattern='^orders$'),
        ],
        states={
            AWAITING_ORDER_DETAILS: [
                CallbackQueryHandler(show_order, pattern=r'^order_\d+$'),
                CallbackQueryHandler(
                    check_delivery_status, pattern=r'^delivery_\d+$'
                ),
                CallbackQueryHandler(
                    edit_order_address, pattern=r'^edit_addr_\d+$'
                ),
                CallbackQueryHandler(repeat_order, pattern=r'^repeat_\d+$'),
                CallbackQueryHandler(back_to_list, pattern=r'^back_to_list$'),
                CallbackQueryHandler(show_order, pattern=r'^order_\d+$'),
            ],
            AWAITING_NEW_ADDRESS: [
                CallbackQueryHandler(
                    set_existing_address, pattern=r'^set_addr_\d+_\d+$'
                ),
                CallbackQueryHandler(
                    ask_new_address_input, pattern=r'^ask_new_addr_\d+$'
                ),
                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND
                    & (~filters.UpdateType.EDITED),
                    handle_new_address_input,
                ),
                CallbackQueryHandler(
                    cancel_new_addr_input, pattern=r'^cancel_new_addr_input$'
                ),
                CallbackQueryHandler(
                    repeat_set_existing_address,
                    pattern=r'^repeat_set_addr_\d+_\d+$',
                ),
                CallbackQueryHandler(
                    repeat_ask_new_address_input,
                    pattern=r'^repeat_ask_new_\d+$',
                ),
                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND
                    & (~filters.UpdateType.EDITED),
                    repeat_handle_new_address_input,
                ),
                CallbackQueryHandler(
                    repeat_cancel_address, pattern=r'^repeat_cancel_addr_\d+$'
                ),
                CallbackQueryHandler(
                    repeat_back_to_choice,
                    pattern=r'^repeat_back_to_choice_\d+$',
                ),
                CallbackQueryHandler(show_order, pattern=r'^order_\d+$'),
            ],
        },
        fallbacks=[CallbackQueryHandler(cancel_and_cleanup, pattern='^back$')],
        allow_reentry=True,
    )
    application.add_handler(conv_handler)
