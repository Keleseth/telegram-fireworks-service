# Модуль с кнопками Акций и скидок для телеграм бота
# TODO: чтобы интегрировать логику работы кнопок в main.py,
# нужно просто импортировать главный обработчик promotions_handler
# и в файле main.py в функции button поместить условие:
# elif data == 'promotions' or data.startswith(
#   ('promo_page_', 'promo_detail_')
# ):
#   await promotions_handler(update, context)


from datetime import datetime, timedelta

from aiohttp import ClientSession
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

API_URL = 'http://127.0.0.1:8000'
ITEMS_PER_PAGE = 5


MOCK_FIREWORKS = {
    101: {'id': 101, 'name': "Ракета 'Метеор'", 'price': 1500},
    102: {'id': 102, 'name': "Фонтан 'Сияние'", 'price': 2300},
    103: {'id': 103, 'name': "Петарды 'Гром'", 'price': 500},
    104: {'id': 104, 'name': "Римская свеча 'Палитра'", 'price': 1200},
    105: {'id': 105, 'name': "Батарея салютов 'Феерия'", 'price': 3500},
    106: {'id': 106, 'name': "Вулкан 'Этна'", 'price': 1800},
    107: {'id': 107, 'name': "Свечи 'Звездопад'", 'price': 900},
    108: {'id': 108, 'name': "Фонтаны 'Радуга'", 'price': 2100},
    109: {'id': 109, 'name': "Ракета 'Комета'", 'price': 1700},
    110: {'id': 110, 'name': "Бенгальские огни 'Кристалл'", 'price': 600},
}

# Тестовые данные для акций (10 штук)
MOCK_DISCOUNTS = [
    {
        'id': 1,
        'name': 'Новогодний Сюрприз',
        'description': 'Скидка 30% на все ракеты',
        'end_date': (datetime.now() + timedelta(days=7)).isoformat(),
        'fireworks': [101, 109],  # Ракеты
    },
    {
        'id': 2,
        'name': 'Чёрная Пятница',
        'description': '2 товара по цене 1',
        'end_date': (datetime.now() + timedelta(days=3)).isoformat(),
        'fireworks': [103, 110],  # Петарды и огни
    },
    {
        'id': 3,
        'name': 'Зимняя Распродажа',
        'description': 'Скидка 25% на фонтаны',
        'end_date': (datetime.now() + timedelta(days=5)).isoformat(),
        'fireworks': [102, 108],  # Фонтаны
    },
    {
        'id': 4,
        'name': "Акция 'Счастливый Час'",
        'description': 'Все товары со скидкой 15%',
        'end_date': (datetime.now() + timedelta(hours=12)).isoformat(),
        'fireworks': [104, 105, 106],  # Разные типы
    },
    {
        'id': 5,
        'name': 'Феерверк-Комбо',
        'description': 'Набор из 3 товаров за 5000₽',
        'end_date': (datetime.now() + timedelta(days=2)).isoformat(),
        'fireworks': [101, 103, 107],  # Комплект
    },
    {
        'id': 6,
        'name': 'Скидка на Вулканы',
        'description': 'Вулканы по цене 1500₽',
        'end_date': (datetime.now() + timedelta(days=4)).isoformat(),
        'fireworks': [106],  # Только вулканы
    },
    {
        'id': 7,
        'name': "Акция 'Красный Цвет'",
        'description': 'Красные фейерверки -20%',
        'end_date': (datetime.now() + timedelta(days=1)).isoformat(),
        'fireworks': [102, 105],  # Красные изделия
    },
    {
        'id': 8,
        'name': 'День Рождения',
        'description': 'Подарок к каждому заказу',
        'end_date': (datetime.now() + timedelta(days=10)).isoformat(),
        'fireworks': [101, 110],  # Подарочные наборы
    },
    {
        'id': 9,
        'name': 'Вечерняя Акция',
        'description': 'Скидки после 18:00',
        'end_date': (datetime.now() + timedelta(hours=6)).isoformat(),
        'fireworks': [104, 107, 109],  # Вечерние товары
    },
    {
        'id': 10,
        'name': 'Мега-Распродажа',
        'description': 'Скидки до 50%',
        'end_date': (datetime.now() + timedelta(days=14)).isoformat(),
        'fireworks': list(MOCK_FIREWORKS.keys()),  # Все товары
    },
]


async def promotions_handler(update: Update, context: CallbackContext):
    """Главный обработчик для акций."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'promotions':
        # Первый вход в раздел акций
        await show_promotions_list(update, context)
    elif data.startswith('promo_page_'):
        # Обработка пагинации
        page = int(data.split('_')[2])
        await show_promotions_list(update, context, page)
    elif data.startswith('promo_detail_'):
        # Показ деталей акции
        promo_id = int(data.split('_')[2])
        await show_promo_details(update, context, promo_id)
    elif data == 'promo_back':
        # Возврат к списку акций
        await show_promotions_list(update, context)


async def show_promotions_list(
    update: Update, context: CallbackContext, page: int = 1
):
    """Показать список акций с пагинацией."""
    try:
        async with ClientSession() as session:
            async with session.get(
                'http://127.0.0.1:8000/discounts'
            ) as response:
                # response = await session.get(
                #     'http://127.0.0.1:8000/discounts',
                # )
                discounts = await response.json()
        # try:
        #     discounts = MOCK_DISCOUNTS

        total_pages = (len(discounts) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        start_idx = (page - 1) * ITEMS_PER_PAGE
        current_discounts = discounts[start_idx : start_idx + ITEMS_PER_PAGE]

        buttons = []
        for discount in current_discounts:
            end_date = datetime.fromisoformat(discount['end_date']).strftime(
                '%d.%m.%Y'
            )
            buttons.append([
                InlineKeyboardButton(
                    f'{discount["type"]} (до {end_date})',
                    callback_data=f'promo_detail_{discount["id"]}',
                )
            ])

        # Пагинация
        if len(discounts) > ITEMS_PER_PAGE:
            pagination = []
            if page > 1:
                pagination.append(
                    InlineKeyboardButton(
                        '◀️', callback_data=f'promo_page_{page - 1}'
                    )
                )
            pagination.append(
                InlineKeyboardButton(
                    f'{page}/{total_pages}', callback_data=' '
                )
            )
            if page < total_pages:
                pagination.append(
                    InlineKeyboardButton(
                        '▶️', callback_data=f'promo_page_{page + 1}'
                    )
                )
            buttons.append(pagination)

        # Навигация
        buttons.append([
            InlineKeyboardButton('🔙 Назад', callback_data='back'),
            InlineKeyboardButton('🏠 Главная', callback_data='back'),
        ])

        text = '🎁 Акции и скидки:\n\n' + '\n'.join(
            f'• {d["type"]} - {d["description"]}' for d in current_discounts
        )

        await update.callback_query.edit_message_text(
            text=text, reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as error:
        raise error


async def show_promo_details(
    update: Update, context: CallbackContext, promo_id: int
):
    """Показать товары акции."""
    try:
        async with ClientSession() as session:
            async with session.get(
                f'http://127.0.0.1:8000/discounts/{promo_id}'
            ) as response:
                # response = await session.get(
                #     f'{API_URL}/discounts/{promo_id}',
                # )
                fireworks = await response.json()
                for firework in fireworks:
                    for key, value in firework.items():
                        print(key, value)
        # кнопки возвращают id фейерверка
        buttons = [
            [
                InlineKeyboardButton(
                    f'{f["name"]} - {f["price"]}₽',
                    callback_data=f'firework_{f["id"]}',
                )
            ]
            for f in fireworks
        ]

        buttons.append([
            InlineKeyboardButton(
                '🔙 К списку акций', callback_data='promotions'
            ),
            InlineKeyboardButton('🏠 Главная', callback_data='back'),
        ])

        await update.callback_query.edit_message_text(
            text='🎆 Акционные товары:',
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    except Exception as e:
        raise e


async def handle_error(update: Update, context: CallbackContext):
    error_text = '⚠️ Произошла ошибка. Попробуйте позже.'
    await update.callback_query.edit_message_text(text=error_text)
