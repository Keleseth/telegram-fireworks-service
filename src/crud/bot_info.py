from src.crud.base import CRUDBase
from src.models.bot_info import BotInfo


class BotInfoCRUD(CRUDBase):
    pass


bot_info_crud = BotInfoCRUD(BotInfo)
