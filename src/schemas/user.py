from datetime import date

import phonenumbers
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)
from pydantic.types import PositiveInt
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserRead(BaseModel):
    """Схема чтения пользователя (возвращаемые данные)."""

    email: EmailStr | None = Field(None, title='Почта пользователя.')
    name: str = Field(..., title='Имя пользователя.')
    nickname: str | None = Field(None, title='Никнейм пользователя.')
    birth_date: date | None = Field(None, title='Дата рождения пользователя.')
    phone_number: PhoneNumber | None = Field(
        None, title='Номер телефона пользователя.'
    )
    age_verified: bool = Field(..., title='Подтверждён ли возраст (18+).')

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Схема создания обычного пользователя через Telegram."""

    telegram_id: PositiveInt = Field(..., title='Телеграмм id пользователя.')
    name: str = Field(..., title='Имя пользователя.')
    nickname: str | None = Field(None, title='Никнейм пользователя.')
    age_verified: bool = Field(
        False,
        title='Подтверждение возвраста',
        description='True, если пользователю больше 18!',
    )


class BaseUserUpdate(BaseModel):
    """Базовая схема обновления профиля пользователя."""

    email: EmailStr | None = Field(None, title='Почта пользователя.')
    name: str | None = Field(None, title='Имя пользователя.')
    nickname: str | None = Field(None, title='Никнейм пользователя.')
    birth_date: date | None = Field(None, title='Дата рождения пользователя.')
    phone_number: str | None = Field(
        None, title='Номер телефона пользователя.'
    )

    @model_validator(mode='after')
    def validate_birth_date_and_age_verified(self) -> 'BaseUserUpdate':
        """Валидация даты рождения пользователя."""
        if self.birth_date is None:
            return self
        today = date.today()
        birth_date = self.birth_date
        if birth_date > today:
            raise ValueError('Дата рождения не может быть в будущем!')
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )
        if age < 0:
            raise ValueError(
                'Некорректная дата рождения: '
                'возраст не может быть отрицательным!'
            )
        if age > 120:
            raise ValueError(
                'Слишком старая дата рождения! '
                'Возраст не может быть больше 120 лет.'
            )
        return self

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            phone = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(phone):
                raise ValueError('Неверный номер телефона')
            return phonenumbers.format_number(
                phone, phonenumbers.PhoneNumberFormat.E164
            )
        except phonenumbers.NumberParseException:
            raise ValueError('Не удалось распарсить номер телефона')


class UserUpdate(BaseUserUpdate):
    """Схема обновления профиля телеграмм пользователя."""

    pass


class AdminUserUpdate(BaseUserUpdate):
    """Схема обновления профиля админа."""

    password: str | None = Field(None, title='Пароль пользователя.')


class TelegramIDSchema(BaseModel):
    """Схема для извлечения telegram_id из запроса."""

    telegram_id: int


class LoginSchema(BaseModel):
    """Схема для регистрации админа."""

    email: EmailStr = Field(..., alias='username')
    password: str
