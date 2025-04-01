import logging
from typing import Optional

import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from src.bot.utils import (
    API_BASE_URL,
    get_user_id_from_telegram,
    return_to_main,
)

logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
AWAITING_ORDER_DETAILS, AWAITING_NEW_ADDRESS = range(2)

# Ключи для context.user_data
DIALOG_DATA = 'dialog_data'

# Статические кнопки
BACK_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton('Назад', callback_data='back')]
])

# Строки сообщений
ORDER_HISTORY_MESSAGE = 'История ваших заказов:\n\n{history_text}'
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
    'Адрес: {address}'
)
PLACE_ORDER_ADDRESS_PROMPT = (
    "Введите адрес доставки (например, 'ул. Ленина 1'):"
)
CANCEL_KEEP_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton('Отменить', callback_data='cancel_keep')]
])

ORDER_ADDRESS_PROMPT = (
    "Введите новый адрес доставки (например, 'ул. Ленина 1'):"
)
ORDER_ADDRESS_UPDATED_MESSAGE = 'Адрес доставки успешно обновлён!'


async def order_history(
    update: Update, context: CallbackContext
) -> Optional[int]:
    query = update.callback_query
    await query.answer()

    user_id = await get_user_id_from_telegram(update)
    if not user_id:
        await query.edit_message_text('Пользователь не найден.')
        return None

    context.user_data[DIALOG_DATA] = {
        'flow': 'order_history',
        'user_id': user_id,
        'telegram_id': update.effective_user.id,
        'order_id': None,
        'step': AWAITING_ORDER_DETAILS,
    }

    async with (
        aiohttp.ClientSession() as session
    ):  # заменили httpx.AsyncClient() на aiohttp.ClientSession()
        async with session.post(
            f'{API_BASE_URL}/orders/me',
            json={'telegram_id': user_id},
        ) as response:
            if response.status != 200:
                await query.edit_message_text(
                    'Ошибка при загрузке истории заказов.'
                )
                return None
            orders = await response.json()

    if not orders:
        await query.edit_message_text('У вас пока нет заказов.')
        return None

    history_text = ''
    keyboard = []
    for order in orders:
        history_text += (
            f'Заказ #{order["id"]} ({order["status"]}):\n'
            f'Состав: {
                chr(10).join(
                    f"{item['firework']['name']}: {item['amount']} шт."
                    for item in order["order_fireworks"]
                )
            }\n'
            f'Итого: {order["total"]} руб.\n'
            f'Адрес: {
                order.get("user_address", {}).get("address", "Не указан")
            }\n'
            f'ФИО: {order.get("fio", "Не указано")}\n'
            f'Телефон: {order.get("phone", "Не указано")}\n'
            f'Звонок оператора: {
                "Да" if order["operator_call"] else "Нет"
            }\n\n'
        )
        keyboard.append([
            InlineKeyboardButton(
                f'Заказ #{order["id"]}', callback_data=f'order_{order["id"]}'
            )
        ])
    keyboard.append([InlineKeyboardButton('Назад', callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        ORDER_HISTORY_MESSAGE.format(history_text=history_text),
        reply_markup=reply_markup,
    )
    return AWAITING_ORDER_DETAILS


async def show_order(
    update: Update, context: CallbackContext
) -> Optional[int]:
    query = update.callback_query
    await query.answer()

    if query.data == 'back':
        return await return_to_main(query)

    order_id = int(query.data.split('_')[1])
    dialog_data = context.user_data.get(DIALOG_DATA, {})
    user_id = dialog_data.get('user_id')

    async with (
        aiohttp.ClientSession() as session
    ):  # заменили httpx.AsyncClient() на aiohttp.ClientSession()
        async with session.post(
            f'{API_BASE_URL}/orders/me', json={'telegram_id': user_id}
        ) as response:
            if response.status != 200:
                await query.edit_message_text('Ошибка при загрузке заказа.')
                return None
            orders = await response.json()
            order = next((o for o in orders if o['id'] == order_id), None)
            if not order:
                await query.edit_message_text('Заказ не найден.')
                return None

    order_summary = '\n'.join(
        f'{item["firework"]["name"]}: {item["amount"]} шт.'
        for item in order['order_fireworks']
    )
    keyboard = []
    if order['status'] != 'Shipped':
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
    keyboard.append([
        InlineKeyboardButton(
            'Узнать статус', callback_data=f'status_{order_id}'
        )
    ])
    if order['status'] == 'Shipped':
        keyboard.append([
            InlineKeyboardButton(
                'Статус доставки', callback_data=f'delivery_{order_id}'
            )
        ])
    keyboard.append([InlineKeyboardButton('Назад', callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        ORDER_DETAILS_MESSAGE.format(
            order_id=order['id'],
            status=order['status'],
            order_summary=order_summary,
            total=order['total'],
            address=order.get('user_address', {}).get('address', 'Не указан'),
            fio=order.get('fio', 'Не указано'),
            phone=order.get('phone', 'Не указано'),
            operator_call='Да' if order['operator_call'] else 'Нет',
        ),
        reply_markup=reply_markup,
    )
    dialog_data['order_id'] = order_id
    dialog_data['step'] = AWAITING_ORDER_DETAILS
    return AWAITING_ORDER_DETAILS


async def check_status(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    order_id = int(query.data.split('_')[1])
    dialog_data = context.user_data.get(DIALOG_DATA, {})
    user_id = dialog_data.get('user_id')

    async with (
        aiohttp.ClientSession() as session
    ):  # заменили httpx.AsyncClient() на aiohttp.ClientSession()
        async with session.post(
            f'{API_BASE_URL}/orders/get',
            json={'order_id': order_id, 'telegram_id': user_id},
        ) as response:
            if response.status != 200:
                await query.edit_message_text('Ошибка при получении статуса.')
                return
            order = await response.json()
    await query.edit_message_text(
        f'Текущий статус заказа #{order_id}: {order["status"]}',
        reply_markup=BACK_KEYBOARD,
    )


async def check_delivery_status(
    update: Update, context: CallbackContext
) -> None:
    query = update.callback_query
    await query.answer()
    order_id = int(query.data.split('_')[1])
    dialog_data = context.user_data.get(DIALOG_DATA, {})
    user_id = dialog_data.get('user_id')

    async with (
        aiohttp.ClientSession() as session
    ):  # заменили httpx.AsyncClient() на aiohttp.ClientSession()
        async with session.get(
            f'{API_BASE_URL}/orders/{order_id}/delivery_status',
            json={'telegram_id': user_id},
        ) as response:
            if response.status != 200:
                await query.edit_message_text(
                    'Ошибка при запросе статуса доставки.'
                )
                return
            data = await response.json()
    await query.edit_message_text(
        f'Статус доставки заказа #{order_id}: {data["delivery_status"]}',
        reply_markup=BACK_KEYBOARD,
    )


async def edit_order_address(
    update: Update, context: CallbackContext
) -> Optional[int]:
    query = update.callback_query
    await query.answer()

    if query.data == 'back':
        return await return_to_main(query)

    order_id = int(query.data.split('_')[2])
    dialog_data = context.user_data.get(DIALOG_DATA, {})
    telegram_id = dialog_data.get('telegram_id')
    dialog_data['order_id'] = order_id

    async with aiohttp.ClientSession() as session:
        async with session.patch(
            f'{API_BASE_URL}/addresses/me',
            json={'telegram_id': telegram_id},
        ) as response:
            if response.status != 200:
                await query.edit_message_text('Ошибка при загрузке адресов.')
                return None
            addresses = response.json()

    if not addresses:
        await query.edit_message_text(ORDER_ADDRESS_PROMPT)
        dialog_data['step'] = AWAITING_NEW_ADDRESS
        return AWAITING_NEW_ADDRESS

    keyboard = [
        [
            InlineKeyboardButton(
                addr['address'],
                callback_data=f'new_addr_{order_id}_{addr["id"]}',
            )
        ]
        for addr in addresses
    ]
    keyboard.append([
        InlineKeyboardButton(
            'Новый адрес', callback_data=f'new_addr_{order_id}'
        )
    ])
    keyboard.append([InlineKeyboardButton('Назад', callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        'Выберите новый адрес доставки:', reply_markup=reply_markup
    )
    dialog_data['step'] = AWAITING_NEW_ADDRESS
    return AWAITING_NEW_ADDRESS


async def handle_new_address(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    dialog_data = context.user_data.get(DIALOG_DATA, {})
    # user_id = dialog_data.get('user_id')
    telegram_id = dialog_data.get('telegram_id')
    order_id = dialog_data.get('order_id')

    if query:
        await query.answer()
        if query.data == 'back':
            return await return_to_main(query)
        if (
            query.data.startswith('new_addr_')
            and len(query.data.split('_')) == 3
        ):
            order_id = int(query.data.split('_')[2])
            await query.edit_message_text(ORDER_ADDRESS_PROMPT)
            dialog_data['order_id'] = order_id
            dialog_data['step'] = AWAITING_NEW_ADDRESS
            return AWAITING_NEW_ADDRESS
        if query.data.startswith('new_addr_'):
            order_id, address_id = map(int, query.data.split('_')[2:4])
        else:
            return None
    else:
        address_text = update.message.text
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{API_BASE_URL}/addresses/',
                json={'address': address_text, 'telegram_id': telegram_id},
            ) as response:
                if response.status != 201:
                    await update.message.reply_text(
                        'Ошибка при сохранении адреса.'
                    )
                    return None
                address_id = response.json()['id']

    async with aiohttp.ClientSession() as session:
        async with session.patch(
            f'{API_BASE_URL}/orders/{order_id}/address',
            json={
                'user_address_id': address_id,
                'operator_call': False,
                'telegram_id': telegram_id,
            },
        ) as response:
            if response.status != 200:
                await (
                    query.edit_message_text
                    if query
                    else update.message.reply_text
                )('Ошибка при обновлении адреса.')
                return None
    await (query.edit_message_text if query else update.message.reply_text)(
        ORDER_ADDRESS_UPDATED_MESSAGE
    )
    context.user_data.pop(DIALOG_DATA, None)
    return 'FINISHED'


async def repeat_order(
    update: Update, context: CallbackContext
) -> Optional[int]:
    query = update.callback_query
    await query.answer()

    if query.data == 'back':
        return await return_to_main(query)

    order_id = int(query.data.split('_')[1])
    dialog_data = context.user_data.get(DIALOG_DATA, {})
    user_id = dialog_data.get('user_id')

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{API_BASE_URL}/orders/{order_id}/repeat_direct',
            json={'telegram_id': user_id},
        ) as response:
            if response.status != 200:
                await query.edit_message_text('Ошибка при повторении заказа.')
                return None
            new_order = response.json()

    dialog_data.update({
        'order_id': new_order['id'],
        'order_summary': '\n'.join(
            f'{item["firework"]["name"]}: {item["amount"]} шт.'
            for item in new_order['order_fireworks']
        ),
        'total': new_order['total'],
        'address': new_order.get('user_address', {}).get(
            'address', 'Не указан'
        ),
        'fio': new_order.get('fio', 'Не указано'),
        'phone': new_order.get('phone', 'Не указано'),
        'step': AWAITING_NEW_ADDRESS,
    })
    telegram_id = dialog_data.get('telegram_id')
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{API_BASE_URL}/addresses/me',
            json={'telegram_id': telegram_id},
        ) as response:
            if response.status != 200:
                await query.edit_message_text('Ошибка при загрузке адресов.')
                return None
            addresses = response.json()

    if not addresses:
        await query.edit_message_text(
            PLACE_ORDER_ADDRESS_PROMPT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('Отменить', callback_data='cancel_keep')]
            ]),
        )
        return None

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
    keyboard.append([
        InlineKeyboardButton('Отменить', callback_data='cancel_keep')
    ])
    await query.edit_message_text(
        'Заказ повторён. Выберите или введите новый адрес:',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return None  # Явный возврат None для согласованности с аннотацией


async def perform_repeat_order(
    query: Update, user_id: str, order_id: int
) -> None:
    # Оставлено для совместимости (пока не решено что делать)
    pass  # Удалено, так как используется прямое повторение


def register_handlers(dp: Application) -> None:
    dp.add_handler(CallbackQueryHandler(order_history, pattern='^orders$'))
    dp.add_handler(CallbackQueryHandler(show_order, pattern=r'^order_\d+$'))
    dp.add_handler(CallbackQueryHandler(check_status, pattern=r'^status_\d+$'))
    dp.add_handler(
        CallbackQueryHandler(check_delivery_status, pattern=r'^delivery_\d+$')
    )
    dp.add_handler(
        CallbackQueryHandler(edit_order_address, pattern=r'^edit_addr_\d+$')
    )
    dp.add_handler(
        CallbackQueryHandler(
            handle_new_address, pattern=r'^new_addr_\d+(_\d+)?$'
        )
    )
    dp.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_address)
    )
    dp.add_handler(CallbackQueryHandler(repeat_order, pattern=r'^repeat_\d+$'))
