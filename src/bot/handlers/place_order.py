import logging
import re
from decimal import Decimal

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

from src.bot.utils import (
    API_BASE_URL,
    get_user_id_from_telegram,
)

logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
(
    AWAITING_CONFIRMATION,
    AWAITING_ADDRESS,
    AWAITING_FIO,
    AWAITING_PHONE,
    AWAITING_OPERATOR,
) = range(5)

# Ключи для context.user_data
DIALOG_DATA = 'dialog_data'

# Статические кнопки
CONFIRM_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Подтвердить', callback_data='confirm_cart'),
        InlineKeyboardButton('Отмена', callback_data='cancel'),
    ]
])
OPERATOR_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Да', callback_data='operator_yes'),
        InlineKeyboardButton('Нет', callback_data='operator_no'),
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
PLACE_ORDER_FIO_PROMPT = "Введите ФИО (например, 'Иван Иванов'):"
PLACE_ORDER_PHONE_PROMPT = "Введите номер телефона (например, '+79991234567'):"
PLACE_ORDER_SUMMARY_MESSAGE = (
    'Ваш заказ:\n{order_summary}\n'
    'Адрес: {address}\n'
    'ФИО: {fio}\n'
    'Телефон: {phone}\n'
    'Итого: {total} руб.\n\n'
    'Хотите получить звонок от оператора для уточнения деталей?'
)
PLACE_ORDER_CONFIRMATION_MESSAGE = (
    'Заказ #{order_id} успешно оформлен!\n'
    'Посмотреть заказ можно в истории заказов.'
)


async def place_order_start(update: Update, context: CallbackContext) -> int:
    """Начало оформления заказа: подтверждение корзины."""
    query = update.callback_query
    await query.answer()

    user_id = await get_user_id_from_telegram(update)
    if not user_id:
        await query.edit_message_text('Пользователь не найден.')
        return ConversationHandler.END

    async with ClientSession() as session:
        async with session.post(
            f'{API_BASE_URL}/user/cart/me',
            json={'telegram_id': update.effective_user.id},
        ) as response:
            if response.status != 200:
                await query.edit_message_text('Не удалось загрузить корзину.')
                return ConversationHandler.END
            cart_items = await response.json()

    if not cart_items:
        await query.edit_message_text('Ваша корзина пуста.')
        return ConversationHandler.END

    cart_summary = '\n'.join(
        f'{item["firework"]["name"]}: {item["amount"]} шт.'
        for item in cart_items
    )
    total = sum(
        item['amount'] * Decimal(item['price_per_unit']) for item in cart_items
    )

    context.user_data[DIALOG_DATA] = {
        'user_id': user_id,
        'telegram_id': update.effective_user.id,
        'cart_items': cart_items,
        'order_summary': cart_summary,
        'total': total,
        'order_id': None,
        'address': None,
        'address_id': None,
        'fio': None,
        'phone': None,
        'operator_call': False,
    }

    await query.edit_message_text(
        PLACE_ORDER_START_MESSAGE.format(
            cart_summary=cart_summary, total=total
        ),
        reply_markup=CONFIRM_KEYBOARD,
    )
    return AWAITING_CONFIRMATION


async def confirm_cart(update: Update, context: CallbackContext) -> int:
    """Подтверждение корзины, создание заказа и запрос адреса."""
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel':
        await query.edit_message_text('Оформление заказа отменено.')
        return ConversationHandler.END

    dialog_data = context.user_data[DIALOG_DATA]
    telegram_id = dialog_data['telegram_id']
    # user_id = dialog_data['user_id']

    # Создаём заказ без адреса
    async with ClientSession() as session:
        async with session.post(
            f'{API_BASE_URL}/orders/',
            json={'telegram_id': telegram_id},
        ) as response:
            if response.status != 200:
                await query.edit_message_text(
                    f'Ошибка при создании заказа: {await response.text()}'
                )
                return ConversationHandler.END
            order = await response.json()
            dialog_data['order_id'] = order['id']

        async with session.post(
            f'{API_BASE_URL}/addresses/me',
            json={'telegram_id': telegram_id},
        ) as response:
            if response.status != 200:
                await query.edit_message_text('Ошибка при загрузке адресов.')
                return ConversationHandler.END
            addresses = await response.json()
            logger.info(f'Addresses response: {addresses}')

    if not addresses:
        await query.edit_message_text(PLACE_ORDER_ADDRESS_PROMPT)
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
    await query.edit_message_text(
        'Выберите адрес доставки:',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return AWAITING_ADDRESS


async def handle_address(update: Update, context: CallbackContext) -> int:
    dialog_data = context.user_data[DIALOG_DATA]

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        telegram_id = str(update.effective_user.id)

        if query.data.startswith('addr_'):
            address_id = query.data.split('_', 1)[1]
            async with ClientSession() as session:
                async with session.get(
                    f'{API_BASE_URL}/addresses/{address_id}',
                    headers={'telegram-id': telegram_id},
                ) as response:
                    if response.status != 200:
                        await query.edit_message_text(
                            'Ошибка при загрузке адреса.'
                        )
                        return ConversationHandler.END

                    address_data = await response.json()

            dialog_data['address'] = address_data['address']
            dialog_data['address_id'] = address_id
            await query.edit_message_text(PLACE_ORDER_FIO_PROMPT)
            return AWAITING_FIO

        if query.data == 'new_addr':
            await query.edit_message_text(PLACE_ORDER_ADDRESS_PROMPT)
            return AWAITING_ADDRESS

        return ConversationHandler.END

    dialog_data['address'] = update.message.text.strip()
    dialog_data['address_id'] = None  # Новый адрес пока не сохранён
    await update.message.reply_text(PLACE_ORDER_FIO_PROMPT)
    return AWAITING_FIO


async def handle_fio(update: Update, context: CallbackContext) -> int:
    """Обработка ввода ФИО."""
    dialog_data = context.user_data[DIALOG_DATA]
    fio = update.message.text.strip()
    if len(fio.split()) < 2:
        await update.message.reply_text('Введите полное ФИО (имя и фамилию).')
        return AWAITING_FIO
    dialog_data['fio'] = fio
    await update.message.reply_text(PLACE_ORDER_PHONE_PROMPT)
    return AWAITING_PHONE


async def handle_phone(update: Update, context: CallbackContext) -> int:
    """Обработка ввода телефона."""
    dialog_data = context.user_data[DIALOG_DATA]
    phone = update.message.text.strip()
    if not re.match(r'^\+7\d{10}$', phone):
        await update.message.reply_text(
            "Введите номер в формате '+79991234567'."
        )
        return AWAITING_PHONE
    dialog_data['phone'] = phone

    summary_text = PLACE_ORDER_SUMMARY_MESSAGE.format(
        order_summary=dialog_data['order_summary'],
        address=dialog_data['address'],
        fio=dialog_data['fio'],
        phone=dialog_data['phone'],
        total=dialog_data['total'],
    )
    await update.message.reply_text(
        summary_text, reply_markup=OPERATOR_KEYBOARD
    )
    return AWAITING_OPERATOR


async def handle_operator_call(
    update: Update, context: CallbackContext
) -> int:
    """Обработка выбора звонка оператора и обновление заказа."""
    query = update.callback_query
    await query.answer()

    dialog_data = context.user_data[DIALOG_DATA]
    dialog_data['operator_call'] = query.data == 'operator_yes'
    # user_id = dialog_data['user_id']
    telegram_id = dialog_data['telegram_id']
    order_id = dialog_data['order_id']

    # Если адрес новый, создаём его через POST /addresses/
    if not dialog_data['address_id']:
        async with ClientSession() as session:
            async with session.post(
                f'{API_BASE_URL}/addresses',
                json={
                    'telegram_id': telegram_id,
                    'address': dialog_data['address'],
                },
            ) as response:
                if response.status != 201:
                    await query.edit_message_text(
                        f'Ошибка при сохранении адреса: '
                        f'{await response.text()}'
                    )
                    return ConversationHandler.END
                address_data = await response.json()
                dialog_data['address_id'] = address_data['id']

    # Обновляем заказ через PATCH /orders/{order_id}/address
    json_data = {
        'user_address_id': dialog_data['address_id'],
        'fio': dialog_data['fio'],
        'phone': dialog_data['phone'],
        'operator_call': dialog_data['operator_call'],
    }
    async with ClientSession() as session:
        async with session.patch(
            f'{API_BASE_URL}/orders/{order_id}/address',
            json={
                'data': json_data,
                'telegram_schema': {'telegram_id': telegram_id},
            },
        ) as response:
            if response.status != 201:
                await query.edit_message_text(
                    f'Ошибка при обновлении заказа: {await response.text()}'
                )
                return ConversationHandler.END

    confirmation_text = PLACE_ORDER_CONFIRMATION_MESSAGE.format(
        order_id=order_id
    )
    if dialog_data['operator_call']:
        confirmation_text += '\nОжидайте звонка оператора.'
    await query.edit_message_text(confirmation_text)
    context.user_data.pop(DIALOG_DATA, None)
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    """Отмена оформления заказа."""
    query = update.callback_query
    await query.answer()
    dialog_data = context.user_data.get(DIALOG_DATA, {})
    if dialog_data.get('order_id'):
        # user_id = dialog_data['user_id']
        order_id = dialog_data['order_id']
        async with ClientSession() as session:
            async with session.patch(
                f'{API_BASE_URL}/orders/{order_id}/status',
                json={
                    'status_id': 3
                },  # "Shipped" как временная заглушка для отмены
            ) as response:
                if response.status != 200:
                    logger.error(
                        f'Failed to cancel order {order_id}: '
                        f'{await response.text()}'
                    )
    await query.edit_message_text('Оформление заказа отменено.')
    context.user_data.pop(DIALOG_DATA, None)
    return ConversationHandler.END


def register_handlers(application: Application) -> None:
    """Регистрация обработчиков для оформления заказа."""
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(place_order_start, pattern='^checkout$')
        ],
        states={
            AWAITING_CONFIRMATION: [
                CallbackQueryHandler(
                    confirm_cart, pattern='^confirm_cart$|^cancel$'
                )
            ],
            AWAITING_ADDRESS: [
                CallbackQueryHandler(
                    handle_address, pattern=r'^addr_\d+$|^new_addr$'
                ),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, handle_address
                ),
            ],
            AWAITING_FIO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_fio)
            ],
            AWAITING_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)
            ],
            AWAITING_OPERATOR: [
                CallbackQueryHandler(
                    handle_operator_call, pattern='^operator_(yes|no)$'
                )
            ],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern='^cancel$')],
    )
    application.add_handler(conv_handler)
