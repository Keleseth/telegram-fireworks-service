from sqladmin import ModelView
from sqlalchemy import select
from sqlalchemy.sql import Select
from starlette.requests import Request

from src.admin.constants import PAGE_SIZE
from src.admin.utils import generate_clickable_formatters
from src.models.product import Firework
from src.models.property import FireworkProperty, PropertyField


class PropertyFieldView(ModelView, model=PropertyField):
    name = 'наименование доп. характеристики товара'
    name_plural = 'Наименования доп. характеристик товаров'

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
    name = 'значение доп. характеристики продукта'
    name_plural = 'Значения доп. характеристик продукта'

    column_list = [
        FireworkProperty.value,
        FireworkProperty.firework,
        FireworkProperty.field,
    ]
    column_details_exclude_list = [
        'id',
        'created_at',
        'updated_at',
        'firework_id',
        'field_id',
    ]
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
    column_filters_enabled = True
    writing_filters = {
        'Фейерверк': 'firework_name',
    }
    column_formatters = generate_clickable_formatters(
        FireworkProperty, '/admin/firework-property/details', column_list
    )

    def list_query(self, request: Request) -> Select:
        stmt = (
            select(FireworkProperty)
            .join(FireworkProperty.firework)
            .join(FireworkProperty.field)
        )

        # обрабатываем фильтр, вводимый вручную
        firework_name = request.query_params.get('firework_name')
        if firework_name:
            stmt = stmt.where(Firework.name.ilike(f'%{firework_name}%'))

        # если вдруг в будущем будут ещё стандартные фильтры
        selected_filters = request.query_params.getlist('filters')
        for f in selected_filters:
            if ':' not in f:
                continue
            field, val = f.split(':', 1)
            val = val.strip().lower()

            if field == 'field':
                stmt = stmt.where(PropertyField.field_name.ilike(f'%{val}%'))

        return stmt

    page_size = PAGE_SIZE
