from pydantic import BaseModel


class ReadBotInfoSchema(BaseModel):
    """Схема для чтения информации о боте."""

    bot_info: str
    about_company: str
    contacts: str
