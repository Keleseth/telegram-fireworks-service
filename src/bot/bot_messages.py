from src.bot.utils import croling_content

EMPTY_DESCRIPTION_MESSAGE = 'Описание в разработке'
EMPTY_PRICE_MESSAGE = 'Цена за товар не указана'
EMPTY_TAGS_MESSAGE = 'Для товара теги не указаны'
EMPTY_PACKING_MATERIAL_MESSAGE = 'Материал упаковки не указан'
EMPTY_DISCOUNS_MESSAGE = 'Скоро появятся 🎆'


FIREWORK_CARD = """
🎆 *{name}* 🎆
────────────────
💰 Цена: {price} ₽
🏷️ Акции: {discounts}
📝 Описание: {description}
────────────────
🏷️ Категория: {category_id}
🏷️ Теги: {tags}
────────────────
⚖️ Единица измерения: {measurement_unit}
📦 Размер продукта: {product_size}
📦 Упаковочный материал: {packing_material}
💥 Количество зарядов: {charges_count}
✨ Количество эффектов: {effects_count}
🔢 Артикул: `{article}`
────────────────
"""

FIREWORK_SHORT_CARD = """
🎆 {name} 🎆
────────────────
💰 Цена: {price} ₽
🏷️ Акции: {discounts}
"""


def build_firework_card(fields: dict, full_info: bool = True) -> str:
    """Заполняет карточку продукта."""
    if not fields['discounts']:
        fields['discounts'] = croling_content(EMPTY_DISCOUNS_MESSAGE)
    else:
        fields['discounts'] = ', '.join([
            f'✅ {discount["type"]}' for discount in fields['discounts']
        ])
    if not full_info:
        return FIREWORK_SHORT_CARD.format(
            name=fields['name'],
            price=croling_content(fields['price']),
            discounts=fields['discounts'],
        )
    if not fields['description']:
        fields['description'] = croling_content(EMPTY_DESCRIPTION_MESSAGE)
    if not fields['price']:
        fields['price'] = croling_content(EMPTY_PRICE_MESSAGE)
    if not fields['tags']:
        fields['tags'] = croling_content(EMPTY_TAGS_MESSAGE)
    else:
        fields['tags'] = ', '.join(
            f'💥 `{tag["name"]}`' for tag in fields['tags']
        )
    if not fields['packing_material']:
        fields['packing_material'] = croling_content(
            EMPTY_PACKING_MATERIAL_MESSAGE
        )
    return FIREWORK_CARD.format(
        name=croling_content(fields['name']),
        code=croling_content(fields['code']),
        price=croling_content(fields['price']),
        discounts=croling_content(fields['discounts']),
        measurement_unit=croling_content(fields['measurement_unit']),
        description=croling_content(fields['description']),
        category_id=croling_content(str(fields['category_id'])),
        product_size=croling_content(fields['product_size']),
        packing_material=croling_content(fields['packing_material']),
        charges_count=croling_content(str(fields['charges_count'])),
        effects_count=croling_content(str(fields['effects_count'])),
        article=croling_content(fields['article']),
        tags=croling_content(fields['tags']),
    )
