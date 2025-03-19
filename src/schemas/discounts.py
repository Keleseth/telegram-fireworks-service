from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from src.models.product import Firework


class BaseDiscountsSchema(BaseModel):
    """Базовая схема акций."""

    id: int
    type: str
    value: Decimal
    start_date: datetime
    end_date: datetime
    description: str
    fireworks: list['Firework']


class ReadDiscountsSchema(BaseDiscountsSchema):
    """Схема для чтения акций."""

    pass


class TelegramIdDiscountsSchema(BaseModel):
    """Схема для передачи телеграм айди."""

    telegram_id: int
