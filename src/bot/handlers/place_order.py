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

from src.bot.utils import API_BASE_URL, get_user_id_from_telegram

logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
(
    AWAITING_CONFIRMATION,
    AWAITING_ADDRESS,
    AWAITING_FIO,
    AWAITING_PHONE,
    AWAITING_OPERATOR,
    AWAITING_SAVE_ADDRESS,
) = range(6)

# Ключи для context.user_data
DIALOG_DATA = 'dialog_data'

# Статические кнопки
CONFIRM_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('✅ Подтвердить', callback_data='confirm_cart'),
        InlineKeyboardButton('❌ Отмена', callback_data='cancel'),
    ]
])
OPERATOR_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('✅ Да', callback_data='operator_yes'),
        InlineKeyboardButton('❌ Нет', callback_data='operator_no'),
    ]
])
SAVE_ADDRESS_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('✅ Да', callback_data='save_yes'),
        InlineKeyboardButton('❌ Нет', callback_data='save_no'),
    ]
])

# Строки сообщений
PLACE_ORDER_START_MESSAGE = (
    '🛒 Ваша корзина:\n\n'
    '{cart_summary}\n\n'
    '💰 Итого: {total} руб.\n\n'
    '⬇️ Подтвердить состав корзины? ⬇️'
)

PLACE_ORDER_ADDRESS_PROMPT = (
    '📍 Введите адрес доставки\n💬 Пример: г. Москва ул. Ленина, д. 1 '
)

PLACE_ORDER_FIO_PROMPT = (
    '📝 Введите ваше ФИО: \n💬 Пример: Иванов Иван Иванович'
)

PLACE_ORDER_PHONE_PROMPT = (
    '📞 Введите номер телефона \n💬 Пример: +79991234567 '
)

PLACE_ORDER_SUMMARY_MESSAGE = (
    '🛍 Ваш заказ: \n\n'
    '{order_summary}\n\n'
    '──────────────\n\n'
    '📍 Адрес: {address}\n'
    '👤 ФИО: {fio}\n'
    '📞 Телефон: {phone}\n'
    '💰 Итого: {total} руб.\n\n'
    '──────────────\n\n'
    '📞 Хотите получить звонок от оператора для уточнения деталей?'
)

PLACE_ORDER_CONFIRMATION_MESSAGE = (
    '✅ Заказ #{order_id} успешно оформлен! \n\n'
    '🔎 Посмотреть заказ можно в истории заказов. \n'
)

SAVE_ADDRESS_PROMPT = (
    '💾 Хотите сохранить этот адрес для будущих заказов? \n🏠 {address} '
)


async def place_order_start(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    user_id = await get_user_id_from_telegram(update)
    if not user_id:
        await query.edit_message_text('🙀 Пользователь не найден ')
        return ConversationHandler.END

    async with ClientSession() as session:
        async with session.post(
            f'{API_BASE_URL}/user/cart/me',
            json={'telegram_id': update.effective_user.id},
        ) as response:
            if response.status != 200:
                await query.edit_message_text(
                    '🆘 - Не удалось загрузить корзину, попробуйте еще'
                )
                return ConversationHandler.END
            cart_items = await response.json()

    if not cart_items:
        await query.edit_message_text(
            'Ваша корзина пуста.😿 '
            'Давай заглянем в каталог и подберём что-нибудь!'
        )
        return ConversationHandler.END

    cart_summary = '\n'.join(
        f'📦 {item["firework"]["name"]}: {item["amount"]} шт.'
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
        'user_address_id': None,  # Убрано address_id как неиспользуемое
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
    query = update.callback_query
    await query.answer()
    if query.data == 'cancel':
        await query.edit_message_text('❌ Оформление заказа отменено.')
        return ConversationHandler.END

    dialog_data = context.user_data[DIALOG_DATA]
    telegram_id = dialog_data['telegram_id']

    async with ClientSession() as session:
        async with session.post(
            f'{API_BASE_URL}/orders/',
            json={'telegram_id': telegram_id},
        ) as response:
            if response.status != 200:
                await query.edit_message_text(
                    f'😿 Ошибка при создании заказа: {await response.text()}'
                )
                return ConversationHandler.END
            order = await response.json()
            dialog_data['order_id'] = order['id']

        async with session.post(
            f'{API_BASE_URL}/useraddresses/me',
            json={'telegram_id': telegram_id},
        ) as response:
            if response.status != 200:
                await query.edit_message_text('😿 Ошибка при загрузке адресов')
                return ConversationHandler.END
            user_addresses = await response.json()
            dialog_data['user_addresses'] = user_addresses
            logger.info(f'User addresses response: {user_addresses}')

    if not user_addresses:
        await query.edit_message_text(PLACE_ORDER_ADDRESS_PROMPT)
        return AWAITING_ADDRESS

    keyboard = [
        [
            InlineKeyboardButton(
                ua['address'], callback_data=f'addr_{ua["user_address_id"]}'
            )
        ]
        for ua in user_addresses
    ]
    keyboard.append([
        InlineKeyboardButton('🏠 Новый адрес', callback_data='new_addr')
    ])
    await query.edit_message_text(
        '🏠 Выберите адрес доставки:',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return AWAITING_ADDRESS


async def handle_address(update: Update, context: CallbackContext) -> int:
    dialog_data = context.user_data[DIALOG_DATA]
    # telegram_id = dialog_data['telegram_id']

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data.startswith('addr_'):
            user_address_id = int(query.data.split('_')[1])
            user_addresses = dialog_data['user_addresses']
            # Используем сохранённые данные
            selected_user_address = next(
                (
                    ua
                    for ua in user_addresses
                    if ua['user_address_id'] == user_address_id
                ),
                None,
            )
            if not selected_user_address:
                await query.edit_message_text('😿 Адрес не найден.')
                return ConversationHandler.END

            dialog_data['address'] = selected_user_address['address']
            dialog_data['user_address_id'] = user_address_id
            await query.edit_message_text(PLACE_ORDER_FIO_PROMPT)
            return AWAITING_FIO
        if query.data == 'new_addr':
            await query.edit_message_text(PLACE_ORDER_ADDRESS_PROMPT)
            return AWAITING_ADDRESS
    dialog_data['address'] = update.message.text.strip()
    dialog_data['user_address_id'] = None
    await update.message.reply_text(PLACE_ORDER_FIO_PROMPT)
    return AWAITING_FIO


async def handle_fio(update: Update, context: CallbackContext) -> int:
    dialog_data = context.user_data[DIALOG_DATA]
    fio = update.message.text.strip()
    if len(fio.split()) < 2:
        await update.message.reply_text(
            '👤 Введите полное ФИО (Имя и Фамилию).'
        )
        return AWAITING_FIO
    dialog_data['fio'] = fio
    await update.message.reply_text(PLACE_ORDER_PHONE_PROMPT)
    return AWAITING_PHONE


async def handle_phone(update: Update, context: CallbackContext) -> int:
    dialog_data = context.user_data[DIALOG_DATA]
    phone = update.message.text.strip()
    if not re.match(r'^\+7\d{10}$', phone):
        await update.message.reply_text(
            '📞 Введите номер в формате: (+79991234567).'
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
    query = update.callback_query
    await query.answer()

    dialog_data = context.user_data[DIALOG_DATA]
    operator_call = query.data == 'operator_yes'
    dialog_data['operator_call'] = operator_call
    telegram_id = dialog_data['telegram_id']
    order_id = dialog_data['order_id']

    json_data = {
        'telegram_schema': {'telegram_id': telegram_id},
        'data': {
            'user_address_id': dialog_data.get('user_address_id'),
            'fio': dialog_data['fio'],
            'phone': dialog_data['phone'],
            'operator_call': operator_call,
        },
    }
    async with ClientSession() as session:
        async with session.patch(
            f'{API_BASE_URL}/orders/{order_id}/address',
            json=json_data,
        ) as response:
            response_text = await response.text()
            logger.info(
                f'PATCH /orders/{order_id}/address response: '
                f'status={response.status}, body={response_text}'
            )
            if response.status not in (200, 201):
                await query.edit_message_text(
                    f'😿 Ошибка при обновлении заказа: {response_text}'
                )
                return ConversationHandler.END

    confirmation_text = PLACE_ORDER_CONFIRMATION_MESSAGE.format(
        order_id=order_id
    )
    if operator_call:
        confirmation_text += '\nОжидайте звонка оператора 😺'
    if not dialog_data.get('user_address_id'):
        await query.edit_message_text(
            confirmation_text
            + f'\n\n{
                SAVE_ADDRESS_PROMPT.format(address=dialog_data["address"])
            }',
            reply_markup=SAVE_ADDRESS_KEYBOARD,
        )
        return AWAITING_SAVE_ADDRESS
    await query.edit_message_text(confirmation_text)
    context.user_data.pop(DIALOG_DATA, None)
    return ConversationHandler.END


async def handle_save_address(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    dialog_data = context.user_data[DIALOG_DATA]
    telegram_id = dialog_data['telegram_id']
    order_id = dialog_data['order_id']

    if query.data == 'save_yes':
        async with ClientSession() as session:
            async with session.post(
                f'{API_BASE_URL}/addresses/',
                json={
                    'telegram_schema': {'telegram_id': telegram_id},
                    'create_data': {
                        'telegram_id': telegram_id,
                        'address': dialog_data['address'],
                    },
                },
            ) as response:
                response_text = await response.text()
                logger.info(
                    f'POST /addresses/ response: '
                    f'status={response.status}, body={response_text}'
                )
                if response.status != 201:
                    logger.error(f'Failed to save address: {response_text}')
                    await query.edit_message_text(
                        '✅ Заказ оформлен, ‼️ но адрес не удалось сохранить'
                    )
                    return ConversationHandler.END
                address_data = await response.json()
                dialog_data['user_address_id'] = address_data[
                    'user_address_id'
                ]

            json_data = {
                'telegram_schema': {'telegram_id': telegram_id},
                'data': {
                    'user_address_id': dialog_data['user_address_id'],
                    'fio': dialog_data['fio'],
                    'phone': dialog_data['phone'],
                    'operator_call': dialog_data['operator_call'],
                },
            }
            async with session.patch(
                f'{API_BASE_URL}/orders/{order_id}/address',
                json=json_data,
            ) as response:
                response_text = await response.text()
                logger.info(
                    f'PATCH /orders/{order_id}/address response: '
                    f'status={response.status}, body={response_text}'
                )
                if response.status not in (200, 201):
                    logger.error(
                        f'Failed to update order with address: {response_text}'
                    )
                    await query.edit_message_text(
                        '✅ Заказ оформлен, ‼️ но адрес не удалось привязать.'
                    )
                    return ConversationHandler.END

        await query.edit_message_text('✅ Заказ оформлен, адрес сохранён!')
    else:
        await query.edit_message_text('✅ Заказ оформлен, адрес не сохранён.')

    context.user_data.pop(DIALOG_DATA, None)
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    dialog_data = context.user_data.get(DIALOG_DATA, {})
    if dialog_data.get('order_id'):
        telegram_id = dialog_data['telegram_id']
        order_id = dialog_data['order_id']
        async with ClientSession() as session:
            async with session.patch(
                f'{API_BASE_URL}/orders/{order_id}/status',
                json={'telegram_id': telegram_id, 'status_id': 3},
            ) as response:
                if response.status != 200:
                    logger.error(
                        f'Failed to cancel order {order_id}:'
                        f' {await response.text()}'
                    )
    await query.edit_message_text('Оформление заказа отменено 💔')
    context.user_data.pop(DIALOG_DATA, None)
    return ConversationHandler.END


def register_handlers(application: Application) -> None:
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
            AWAITING_SAVE_ADDRESS: [
                CallbackQueryHandler(
                    handle_save_address, pattern='^save_(yes|no)$'
                )
            ],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern='^cancel$')],
    )
    application.add_handler(conv_handler)
