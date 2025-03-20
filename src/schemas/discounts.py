from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class BaseDiscountsSchema(BaseModel):
    """Базовая схема акций."""

    id: int
    type: str
    value: Decimal | None = None
    start_date: datetime
    end_date: datetime
    description: str


class ReadDiscountsSchema(BaseDiscountsSchema):
    """Схема для чтения акций."""

    pass


class TelegramIdDiscountsSchema(BaseModel):
    """Схема для передачи телеграм айди."""

    telegram_id: int
