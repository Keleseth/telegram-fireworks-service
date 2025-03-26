import logging

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    Dispatcher,
    MessageHandler,
    filters,
)

from src.bot.utils import (
    API_BASE_URL,
    get_user_id_from_telegram,
    return_to_main,
)

logger = logging.getLogger(__name__)

# Состояния для будущего ConversationHandler
(
    AWAITING_CONFIRMATION,
    AWAITING_ADDRESS,
    AWAITING_CONTACT_INFO,
    AWAITING_OPERATOR,
) = range(4)

# Ключи для context.user_data
DIALOG_DATA = 'dialog_data'

# Статические кнопки
CONFIRM_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Подтвердить', callback_data='confirm_cart'),
        InlineKeyboardButton('Назад', callback_data='back'),
    ]
])
OPERATOR_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Да', callback_data='operator_yes'),
        InlineKeyboardButton('Нет', callback_data='operator_no'),
    ]
])
SAVE_ADDRESS_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Сохранить адрес', callback_data='save_address'),
        InlineKeyboardButton('Не сохранять', callback_data='no_save_address'),
    ]
])

# Строки сообщений
PLACE_ORDER_START_MESSAGE = (
    'Ваша корзина:\n{cart_summary}\n\n'
    'Итого: {total} руб.\n\n'
    'Подтвердить состав корзины?'
)
PLACE_ORDER_ADDRESS_PROMPT = (
    "Введите адрес доставки (например, 'ул. Ленина 1'):"
)
PLACE_ORDER_CONTACT_PROMPT = (
    "Введите ФИО и номер телефона (например, 'Иван Иванов, +79991234567'):"
)
PLACE_ORDER_SUMMARY_MESSAGE = (
    'Ваш заказ:\n{order_summary}\n'
    'Адрес: {address}\n'
    'ФИО: {fio}\n'
    'Телефон: {phone}\n'
    'Итого: {total} руб.\n\n'
    'Хотите получить звонок от оператора '
    'для уточнения деталей заказа?\n'
    'Звонок поступит в течение 15 минут '
    '(с 9:00 до 18:00 МСК) '
    'или до 10:00 следующего дня.'
)
PLACE_ORDER_CONFIRMATION_MESSAGE = (
    'Заказ успешно оформлен! '
    'Ожидайте звонка оператора.\n'
    'Посмотреть заказ можно в истории заказов.'
)
PLACE_ORDER_NO_OPERATOR_MESSAGE = (
    'Заказ успешно оформлен! '
    'Посмотреть можно в истории заказов.\n\n'
    'Сохранить введённый адрес для будущих заказов?'
)


async def place_order_start(update: Update, context: CallbackContext) -> int:
    """Начало оформления заказа: показ корзины."""
    query = update.callback_query
    await query.answer()

    user_id = await get_user_id_from_telegram(update)
    if not user_id:
        await query.edit_message_text('Пользователь не найден.')
        return None

    context.user_data[DIALOG_DATA] = {
        'flow': 'place_order',
        'user_id': user_id,
        'telegram_id': update.effective_user.id,
        'order_id': None,
        'address_id': None,
        'address': None,
        'fio': None,
        'phone': None,
        'operator_call': None,
        'step': AWAITING_CONFIRMATION,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'{API_BASE_URL}/user/cart/me',
            headers={'user-id': user_id},
        )
        if response.status_code != 200:
            await query.edit_message_text('Не удалось загрузить корзину.')
            return None
        cart_items = response.json()

    if not cart_items:
        await query.edit_message_text('Ваша корзина пуста.')
        return None

    cart_summary = '\n'.join(
        f'{item["firework"]["name"]}: {item["amount"]} шт.'
        for item in cart_items
    )
    total = sum(item['amount'] * item['price_per_unit'] for item in cart_items)

    await query.edit_message_text(
        PLACE_ORDER_START_MESSAGE.format(
            cart_summary=cart_summary, total=total
        ),
        reply_markup=CONFIRM_KEYBOARD,
    )
    return AWAITING_CONFIRMATION


async def confirm_cart(update: Update, context: CallbackContext) -> int:
    """Подтверждение корзины и выбор адреса."""
    query = update.callback_query
    await query.answer()

    if query.data == 'back':
        return await return_to_main(query)

    dialog_data = context.user_data.get(DIALOG_DATA, {})
    user_id = dialog_data.get('user_id')
    telegram_id = dialog_data.get('telegram_id')

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'{API_BASE_URL}/orders/', headers={'user-id': user_id}
        )
        if response.status_code != 200:
            await query.edit_message_text('Ошибка при создании заказа.')
            return None
        order = response.json()
        dialog_data['order_id'] = order['id']

        response = await client.post(
            f'{API_BASE_URL}/addresses/me',
            json={'telegram_id': telegram_id},
        )
        if response.status_code != 200:
            await query.edit_message_text('Ошибка при загрузке адресов.')
            return None
        addresses = response.json()

    if not addresses:
        await query.edit_message_text(PLACE_ORDER_ADDRESS_PROMPT)
        dialog_data['step'] = AWAITING_ADDRESS
        return AWAITING_ADDRESS

    keyboard = [
        [
            InlineKeyboardButton(
                addr['address'], callback_data=f'addr_{addr["id"]}'
            )
        ]
        for addr in addresses
    ]
    keyboard.append([
        InlineKeyboardButton('Новый адрес', callback_data='new_addr')
    ])
    keyboard.append([InlineKeyboardButton('Назад', callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        'Выберите адрес доставки:', reply_markup=reply_markup
    )
    dialog_data['step'] = AWAITING_ADDRESS
    return AWAITING_ADDRESS


async def handle_address(update: Update, context: CallbackContext) -> int:
    """Обработка выбора или ввода адреса."""
    query = update.callback_query
    dialog_data = context.user_data.get(DIALOG_DATA, {})
    telegram_id = dialog_data.get('telegram_id')

    if query:
        await query.answer()
        if query.data == 'back':
            return await return_to_main(query)
        if query.data == 'new_addr':
            await query.edit_message_text(PLACE_ORDER_ADDRESS_PROMPT)
            dialog_data['step'] = AWAITING_ADDRESS
            return AWAITING_ADDRESS
        address_id = int(query.data.split('_')[1])
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{API_BASE_URL}/addresses/me',
                json={'telegram_id': telegram_id},
            )
            if response.status_code != 200:
                await query.edit_message_text('Ошибка при загрузке адресов.')
                return None
            addresses = response.json()
            address = next(
                (a['address'] for a in addresses if a['id'] == address_id),
                None,
            )
        dialog_data['address_id'] = address_id
        dialog_data['address'] = address
    else:
        dialog_data['address'] = update.message.text
        # Адрес пока не сохраняем, ждём решения пользователя в конце

    await (query.edit_message_text if query else update.message.reply_text)(
        PLACE_ORDER_CONTACT_PROMPT
    )
    dialog_data['step'] = AWAITING_CONTACT_INFO
    return AWAITING_CONTACT_INFO


async def handle_contact_info(update: Update, context: CallbackContext) -> int:
    """Обработка ввода ФИО и телефона."""
    dialog_data = context.user_data.get(DIALOG_DATA, {})
    user_id = dialog_data.get('user_id')

    try:
        fio, phone = update.message.text.split(', ')
        dialog_data['fio'] = fio
        dialog_data['phone'] = phone
    except ValueError:
        await update.message.reply_text(
            "Ошибка формата. Введите: 'ФИО, +79991234567'"
        )
        return AWAITING_CONTACT_INFO

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f'{API_BASE_URL}/orders/{dialog_data["order_id"]}/address',
            json={
                'user_address_id': dialog_data.get('address_id'),
                'operator_call': False,
            },
            headers={'user-id': user_id},
        )
        if response.status_code != 200:
            await update.message.reply_text('Ошибка при обновлении заказа.')
            return None
        order = response.json()

    order_summary = '\n'.join(
        f'{item["firework"]["name"]}: {item["amount"]} шт.'
        for item in order['order_fireworks']
    )
    total = sum(
        item['amount'] * item['price_per_unit']
        for item in order['order_fireworks']
    )

    await update.message.reply_text(
        PLACE_ORDER_SUMMARY_MESSAGE.format(
            order_summary=order_summary,
            address=dialog_data['address'],
            fio=fio,
            phone=phone,
            total=total,
        ),
        reply_markup=OPERATOR_KEYBOARD,
    )
    dialog_data['order_summary'] = order_summary
    dialog_data['total'] = total
    dialog_data['step'] = AWAITING_OPERATOR
    return AWAITING_OPERATOR


async def handle_operator_call(
    update: Update, context: CallbackContext
) -> str:
    """Окончательное подтверждение с выбором звонка оператора."""
    query = update.callback_query
    await query.answer()

    dialog_data = context.user_data.get(DIALOG_DATA, {})
    user_id = dialog_data.get('user_id')
    operator_call = query.data == 'operator_yes'

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f'{API_BASE_URL}/orders/{dialog_data["order_id"]}/address',
            json={
                'user_address_id': dialog_data.get('address_id'),
                'operator_call': operator_call,
                # Проверить что API примет эти поля
                'fio': dialog_data['fio'],
                'phone': dialog_data['phone'],
                'address': dialog_data['address'],
            },
            headers={'user-id': user_id},
        )
        if response.status_code != 200:
            await query.edit_message_text('Ошибка при обновлении заказа.')
            return None

        if not operator_call:
            response = await client.delete(
                f'{API_BASE_URL}/user/cart/',
                headers={'user-id': user_id},
            )
            if response.status_code != 200:
                logger.warning('Не удалось очистить корзину после заказа.')

    if operator_call:
        await query.edit_message_text(PLACE_ORDER_CONFIRMATION_MESSAGE)
    else:
        await query.edit_message_text(
            PLACE_ORDER_NO_OPERATOR_MESSAGE,
            reply_markup=SAVE_ADDRESS_KEYBOARD
            if not dialog_data.get('address_id')
            else None,
        )
    return 'FINISHED'


async def handle_save_address(update: Update, context: CallbackContext) -> str:
    """Обработка сохранения адреса."""
    query = update.callback_query
    await query.answer()

    dialog_data = context.user_data.get(DIALOG_DATA, {})
    user_id = dialog_data.get('user_id')
    telegram_id = dialog_data.get('telegram_id')

    if query.data == 'save_address':
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{API_BASE_URL}/addresses/',
                json={
                    'address': dialog_data['address'],
                    'telegram_id': telegram_id,
                    'fio': dialog_data['fio'],
                    'phone': dialog_data['phone'],
                },
                headers={'user-id': user_id},
            )
            if response.status_code != 201:
                await query.edit_message_text('Ошибка при сохранении адреса.')
            else:
                await query.edit_message_text(
                    'Адрес сохранён! Посмотреть заказ можно в истории заказов.'
                )

    context.user_data.pop(DIALOG_DATA, None)
    return 'FINISHED'


def register_handlers(dp: Dispatcher) -> None:
    """Временная регистрация хэндлеров до переноса в main.py."""
    dp.add_handler(
        CallbackQueryHandler(place_order_start, pattern='^checkout$')
    )
    dp.add_handler(
        CallbackQueryHandler(confirm_cart, pattern='^confirm_cart$')
    )
    dp.add_handler(CallbackQueryHandler(handle_address, pattern=r'^addr_\d+$'))
    dp.add_handler(CallbackQueryHandler(handle_address, pattern='^new_addr$'))
    dp.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_address,
            lambda u, c: c.user_data.get(DIALOG_DATA, {}).get('step')
            == AWAITING_ADDRESS,
        )
    )
    dp.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_contact_info,
            lambda u, c: c.user_data.get(DIALOG_DATA, {}).get('step')
            == AWAITING_CONTACT_INFO,
        )
    )
    dp.add_handler(
        CallbackQueryHandler(
            handle_operator_call, pattern='^operator_(yes|no)$'
        )
    )
    dp.add_handler(
        CallbackQueryHandler(
            handle_save_address, pattern='^(save|no_save)_address$'
        )
    )
