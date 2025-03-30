from sqladmin import ModelView

from src.admin.constants import PAGE_SIZE
from src.admin.utils import generate_clickable_formatters
from src.models.property import FireworkProperty, PropertyField


class PropertyFieldView(ModelView, model=PropertyField):
    name = 'доп. характеристики'
    name_plural = 'Доп. характеристики'

    column_list = [
        'field_name',
    ]
    column_details_exclude_list = [
        'id',
        'created_at',
        'updated_at',
    ]
    form_excluded_columns = [
        'id',
        'created_at',
        'updated_at',
    ]
    column_labels = {
        'field_name': 'тип характеристики',
    }
    column_formatters = generate_clickable_formatters(
        PropertyField, '/admin/property-field/details', column_list
    )

    page_size = PAGE_SIZE


class FireworkPropertyView(ModelView, model=FireworkProperty):
    name = 'характеристика'
    name_plural = 'Характеристики'

    name = 'Доп. характеристика продукта'
    name_plural = 'Значения доп. характеристик'

    column_list = [
        FireworkProperty.value,
        FireworkProperty.firework,
        FireworkProperty.field,
    ]
    # column_details_exclude_list = [
    #     'id',
    #     'created_at',
    #     'updated_at',
    #     'firework_id',
    #     'field_id'
    # ]
    # column_details_list = [
    #     'value',
    #     'firework',
    #     'field',
    # ]
    form_excluded_columns = [
        'id',
        'created_at',
        'updated_at',
    ]
    column_labels = {
        'value': 'характеристика',
        'firework': 'продукт',
        'field': 'тип характеристики',
    }
    column_formatters = generate_clickable_formatters(
        FireworkProperty, '/admin/firework-property/details', column_list
    )

    page_size = PAGE_SIZE
