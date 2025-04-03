import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseJFModel

if TYPE_CHECKING:
    from src.models import Tag


class AccountAge(enum.Enum):
    LESS_3_MONTHS = 'less_3_months'
    FROM_3_TO_12_MONTHS = 'from_3_to_12_months'
    FROM_1_TO_3_YEARS = 'from_1_to_3_years'
    MORE_THAN_3_YEARS = 'more_than_3_years'

    def __str__(self) -> str:
        return {
            self.LESS_3_MONTHS: 'моложе 3 месяцев',
            self.FROM_3_TO_12_MONTHS: 'от 3 месяцев до года',
            self.FROM_1_TO_3_YEARS: 'от года до 3 лет',
            self.MORE_THAN_3_YEARS: 'от 3 лет и старше',
        }[self]


class Newsletter(BaseJFModel):
    """Основная модель для рассылок.

    Поля:
        1. id: int - primary key.
        2. content: str - текст рассылки, информация о новостях и т.п.
        3. datetime_send: datetime - дата отправки.
        4. switch_send: bool - статус отправки.
        5. mediafiles: list['NewsletterMedia'] поле для связи.
           с моделью NewsletterMedia.
        6. age_verified: bool - поле фильтрации юзеров по совершеннолетию.
        7. canceled: bool - флаг, отменить ли рассылку.
        5. tags: list['Tag'] поле списка связанных объектов модели Tag.
    """

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    content: Mapped[str]
    number_of_orders: Mapped[int] = mapped_column(Integer, default=0)
    age_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    mediafiles: Mapped[list['NewsletterMedia']] = relationship(
        secondary='newslettermedialink',
        back_populates='newsletters',
        lazy='selectin',
    )
    tags: Mapped[list['Tag']] = relationship(
        'Tag',
        secondary='newslettertag',
        back_populates='newsletters',
        lazy='selectin',
    )
    datetime_send: Mapped[datetime]
    switch_send: Mapped[bool] = mapped_column(
        default=False,
        server_default=text('false'),
    )
    account_age: Mapped[AccountAge | None] = mapped_column(
        SQLEnum(AccountAge, name='account_age_enum'), nullable=True
    )
    users_related_to_tag: Mapped[bool | None]
    canceled: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        max_len = 30
        if len(self.content) <= max_len:
            return self.content
        cut = self.content[:max_len]
        if ' ' in cut:
            cut = cut[: cut.rfind(' ')]
        return f'{cut}...'


class NewsletterMediaLink(BaseJFModel):
    """Промежуточная модель для связи Newsletter и NewsletterMedia."""

    newsletter_id: Mapped[int] = mapped_column(
        ForeignKey('newsletter.id'), primary_key=True
    )
    media_id: Mapped[int] = mapped_column(
        ForeignKey('newslettermedia.id'), primary_key=True
    )


class NewsletterMedia(BaseJFModel):
    """Модель для медиа файлов рассылок."""

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    media_url: Mapped[str]

    newsletters: Mapped[list['Newsletter']] = relationship(
        secondary='newslettermedialink',
        back_populates='mediafiles',
        lazy='selectin',
    )

    def __repr__(self) -> str:
        return self.media_url


class NewsletterTag(BaseJFModel):
    """Промежуточная модель many-to-many.

    Поля:
        1. tag_id: id тега.
        2. newsletter_id: id рассылки.

    Связывает между собой модели Tag и Newsletter.
    """

    tag_id: Mapped[int] = mapped_column(ForeignKey('tag.id'), primary_key=True)
    newsletter_id: Mapped[int] = mapped_column(
        ForeignKey('newsletter.id'), primary_key=True
    )
