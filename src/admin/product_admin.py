from sqladmin import ModelView

# from sqladmin.filters import FilterEqual, FilterLike, FilterIn
from src.models.product import Firework


class FireworkAdmin(ModelView, model=Firework):
    """Представление фейерверков в админке."""

    name = 'Фейерверк'
    name_plural = 'Фейерверки'

    column_list = [
        Firework.id,
        Firework.name,
        Firework.price,
        Firework.category,
        Firework.tags,
    ]

    column_searchable_list = ['name', 'article', 'code']

    column_sortable_list = ['id', 'name', 'price']

    # фильтрация объектов по полям включая relationship поля.
    column_filters = [
        'name',
    ]
    column_default_sort = 'id'

    page_size = 10
    column_filters_enabled = True

    # замена отображаемых имен включая relationship поля.
    column_labels = {
        'id': 'ID',
        'name': 'Название',
        'price': 'Цена',
        'category': 'Категория',
        'tags': 'Теги',
    }
