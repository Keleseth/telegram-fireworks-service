import inspect

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
)

from src.bot.keyboards import menu
from src.bot.states import (
    ALL_CATALOG,
    CATALOG,
    CATALOG_MENU_INLINE_HANDLER,
    CATEGORY_INLINE_HANDLER,
)
from src.schemas.filter_shema import FireworkFilterSchema

navigation_keyboard = [
    [InlineKeyboardButton('Весь каталог', callback_data='all_catalog')],
    [InlineKeyboardButton('Категории', callback_data='categories')],
    [InlineKeyboardButton('Подбор по параметрам', callback_data='parameters')],
    [InlineKeyboardButton('Назад', callback_data='back')]
]


def build_filter_params_keyboard(
    filter_param_name: str
):
    keyboard = [
        [InlineKeyboardButton('Назад', callback_data=f'back_to_{filter_param_name}')]
    ]
    return InlineKeyboardMarkup(keyboard)


def build_cart_and_favorite_keyboard(
    firework_id: str
):
    keyboard = [
        [InlineKeyboardButton(
            'В корзину',
            callback_data=f'add_to_cart_{firework_id}'
        )],
        [InlineKeyboardButton(
            'В избранное',
            callback_data=f'add_to_favorite_{firework_id}'
        )]
    ]
    return keyboard


async def catalog_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создает меню каталога товаров."""
    await update.callback_query.edit_message_text(
        'Каталог продуктов: ',
        reply_markup=InlineKeyboardMarkup(navigation_keyboard)
    )
    return CATALOG_MENU_INLINE_HANDLER


async def catalog_menu_inline_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    option = query.data
    if option == 'all_catalog':
        return await show_all_catalog(update, context)
    if option == 'categories':
        return await show_categories(update, context)
    if option == 'parameters':
        await query.edit_message_text('parameters')
        return CATALOG
    if option == 'back_to_catalog':
        return await catalog_menu(update, context)
    return await menu(update, context)


async def show_all_catalog(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    fireworks = ['Товар1', 'Товар2']
    i = 0
    for firework in fireworks:
        await update.callback_query.message.reply_text(
            firework,
            reply_markup=InlineKeyboardMarkup(
                build_cart_and_favorite_keyboard(firework_id=i)
            )
        )
        i += 1
    await update.callback_query.message.reply_text(
        'Вернуться в меню каталога:',
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Назад', callback_data='back_to_catalog')]]
        )
    )
    return CATALOG_MENU_INLINE_HANDLER


async def show_all_catalog_inline_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    option = query.data
    if option.startswith('add_to_card_'):
        # TODO добавить в корзину
        return ConversationHandler.END
    if option.startswith('add_to_favorite_'):
        # TODO добавить в избранное
        return ConversationHandler.END
    return await catalog_menu(update, context)


async def show_categories(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    categories = ['Category1', 'Category2']
    i = 0
    for category in categories:
        keyboard = [
            [
                InlineKeyboardButton(
                    category,
                    callback_data=f'category_{i}'
                )
                for category in categories
            ]
        ]
        # reply_markup = InlineKeyboardMarkup(keyboard)
        i += 1
    keyboard.append(
        [InlineKeyboardButton('Назад', callback_data='back_to_catalog')]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        'Выберете категорию товара:',
        reply_markup=reply_markup
    )
    return CATEGORY_INLINE_HANDLER


async def back_to_categories(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    return await show_categories(update, context)


async def show_categories_inline_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    option = query.data
    if option.startswith('category_'):
        return await show_categories_fireworks(update, context)
    return await show_categories(update, context)


async def show_categories_fireworks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    category_id = update.callback_query.data.split('_')[-1]
    # TODO обращение к БД
    fireworks = ['Firework_category1', 'Firework_category2']
    for firework in fireworks:
        keyboard = [
            [
                InlineKeyboardButton(
                    'В корзину',
                    callback_data=f'add_to_cart_{firework}'
                ),
                InlineKeyboardButton(
                    'В избранное',
                    callback_data=f'add_to_favorite_{firework}'
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text(
            firework, reply_markup=reply_markup
        )
    await update.callback_query.message.reply_text(
        'Вернуться к категориям:',
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Назад', callback_data='back_to_categories')]]
        )
    )


catalog_states = {
    CATALOG: [CallbackQueryHandler(catalog_menu)],
    CATALOG_MENU_INLINE_HANDLER: [CallbackQueryHandler(catalog_menu_inline_handler)],
    ALL_CATALOG: [CallbackQueryHandler(show_all_catalog)],
    CATEGORY_INLINE_HANDLER: [CallbackQueryHandler(show_categories_inline_handler)]
}


async def selection_by_parameters(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    await update.callback_query.edit_message_text(
        'Укажите название товара'
    )
    return NAME


async def select_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['filter'] = FireworkFilterSchema(
        name=update.message.text
    )
    await update.message.reply_text(
        'Укажите количество зарядов:',
        reply_markup=build_filter_params_keyboard(
            inspect.currentframe().f_code.co_name
        )
    )
    return CHARGES_COUNT


async def skip_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['filter'] = FireworkFilterSchema()
    await update.message.reply_text(
        'Укажите количество зарядов:',
        reply_markup=build_filter_params_keyboard(
            inspect.currentframe().f_code.co_name
        )
    )
    return CHARGES_COUNT


async def select_charges_count(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['filter'].charges_count = int(update.message.text)
    await update.message.reply_text(
        'Введите категории:',
        reply_markup=build_filter_params_keyboard(
            inspect.currentframe().f_code.co_name
        )
    )
    return CATEGORIES


async def skip_charges_count(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        'Укажите категории:',
        reply_markup=build_filter_params_keyboard(
            inspect.currentframe().f_code.co_name
        )
    )
    return CATEGORIES


async def select_categories(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    # TODO оптимизировать парсинг категорий из сообщения пользователя
    context.user_data['filter'].categories = [
        category for category in update.message.text.split()
    ]
    await update.message.reply_text(
        'Введите артикул:',
        reply_markup=build_filter_params_keyboard(
            inspect.currentframe().f_code.co_name
        )
    )
    return ARTICLE


async def skip_categories(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        'Введите артикул:',
        reply_markup=build_filter_params_keyboard(
            inspect.currentframe().f_code.co_name
        )
    )
    return ARTICLE


async def select_article(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['filter'].article = update.message.text
    await update.message.reply_text(
        'Укажите теги товаров:',
        reply_markup=build_filter_params_keyboard(
            inspect.currentframe().f_code.co_name
        )
    )
    return TAGS


async def skip_article(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        'Укажите теги товаров:',
        reply_markup=build_filter_params_keyboard(
            inspect.currentframe().f_code.co_name
        )
    )
    return TAGS


async def select_tags(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    tag_names = []
    context.user_data['filter'].tags = [
        tag_name for tag_name in tag_names
    ]
    await update.message.reply_text(
        'Укажите минимальную цену товаров:',
        reply_markup=build_filter_params_keyboard(
            inspect.currentframe().f_code.co_name
        )
    )
    return MIN_PRICE


async def skip_tags(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        'Укажите минимальную цену товаров:',
        reply_markup=build_filter_params_keyboard(
            inspect.currentframe().f_code.co_name
        )
    )
    return MIN_PRICE


async def select_min_price(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['filter'].min_price = update.message.text
    await update.message.reply_text(
        'Укажите максимальную цену товаров:',
        reply_markup=build_filter_params_keyboard(
            inspect.currentframe().f_code.co_name
        )
    )
    return MAX_PRICE


async def skip_min_price(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        'Укажите максималую цену товаров:',
        reply_markup=build_filter_params_keyboard(
            inspect.currentframe().f_code.co_name
        )
    )
    return MAX_PRICE


async def select_max_price(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['filter'].max_price = update.message.text
    await update.message.reply_text(
        'Укажите параметры для сортировки товаров:',
        reply_markup=build_filter_params_keyboard(
            inspect.currentframe().f_code.co_name
        )
    )
    return ORDER_BY


async def skip_max_price(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        'Укажите параметры для сортировки товаров:',
        reply_markup=build_filter_params_keyboard(
            inspect.currentframe().f_code.co_name
        )
    )
    return ORDER_BY


async def select_order_by(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    orders_by = [
        order_by for order_by in update.message.text
    ]
    context.user_data['filter'].order_by = orders_by
    await apply_filters(update, context)
    return ConversationHandler.END


async def skip_order_by(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await apply_filters(update, context)
    return ConversationHandler.END


async def apply_filters(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    filter_data = context.user_data['filter_data']
    # TODO запрашиваем у API get_multi с filter_schema
    fireworks = []
    if fireworks:
        for firework in fireworks:
            await update.message.reply_text(
                firework,
                reply_markup=InlineKeyboardMarkup(
                    build_cart_and_favorite_keyboard(firework_id=firework['id'])
                )
            )
    else:
        await update.message.reply_text(
            'Товары по вашему запросу не найдены('
        )


async def back_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()


def register_handlers(application):
    conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler()]
    )
