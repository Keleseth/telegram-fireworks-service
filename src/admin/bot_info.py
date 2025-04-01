from sqladmin import ModelView

from src.models.bot_info import BotInfo


class BotInfoView(ModelView, model=BotInfo):
    name = 'информация о боте'
    name_plural = 'Информация о боте'

    column_list = [BotInfo.bot_info, BotInfo.about_company, BotInfo.contacts]
    column_details_list = ['bot_info', 'about_company', 'contacts']
    form_excluded_columns = [
        'id',
        'updated_at',
        'created_at',
    ]
    column_labels = {
        'bot_info': 'информация о бота',
        'about_company': 'информация о компании',
        'contacts': 'контакты',
    }
