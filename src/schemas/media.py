from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl

MEDIA_BASE_SCHEMA_TITLE = 'Базовый класс Pydantic-схемы для модели Media'
MEDIA_DB_SCHEMA_TITLE = 'Схема для отображения медиа в ответе сервера'
MEDIA_CREATE_SCHEMA_TITLE = 'Схема для создания медиа'
MEDIA_UPDATE_SCHEMA_TITLE = 'Схема для обнвления медиа'

MEDIA_URL_MIN_LENGTH = 1
MEDIA_URL_MAX_LENGTH = 2**11
MEDIA_URL_TITLE = 'Ссылка на медиа-файл'

MEDIA_TYPE_MIN_LENGTH = 1
MEDIA_TYPE_MAX_LENGTH = 64
MEDIA_TYPE_TITLE = 'Тип медиа-файла'

CREATED_AT_TITLE = 'Дата и время создания медиа'

UPDATED_AT_TITLE = 'Дата и время последнего редактирования медиа'

CORRECT_REQUEST = {
    'summary': 'Корректный запрос',
    'description': 'Все параметры запроса корректны',
    'value': {
        'media_url': 'https://my_media_url',
        'media_type': 'my_media_type',
    },
}

CORRECT_REQUEST_WITHOUT_MEDIA_TYPE = {
    'summary': 'Корректный запрос',
    'description': 'Все параметры запроса корректны',
    'value': {'media_url': 'https://my_media_url'},
}

INVALID_EMPTY_BODY_REQUEST = {
    'summary': 'Запрос с пустым телом',
    'description': 'Все параметры запроса корректны',
    'value': {},
}
INVALID_MEDIA_URL_FORMAT_REQUEST = {
    'summary': 'Запрос с неправильным форматом media_url',
    'description': 'Все параметры запроса корректны',
    'value': {
        'media_url': 'error_protocol://my_media_url',
        'media_type': 'media_type_of_invalid_media',
    },
}


class MediaBase(BaseModel):
    """Базовая схема для модели Media.

    Аргументы:
        media_url (HttpUrl): ссылка на медиа-файл.
        media_type (str): тип медиа-файла.

    Используется для наследования этих полей в дочерние схемы.
    """

    media_url: HttpUrl = Field(
        None,
        min_length=MEDIA_URL_MIN_LENGTH,
        max_length=MEDIA_URL_MAX_LENGTH,
        title=MEDIA_URL_TITLE,
    )
    media_type: str = Field(
        None,
        min_length=MEDIA_TYPE_MIN_LENGTH,
        max_length=MEDIA_TYPE_MAX_LENGTH,
        title=MEDIA_TYPE_TITLE,
    )

    class Config:
        """Конфигурация Pydantic для схемы MediaBase.

        Поля:
            title: заголовок схемы.
        """

        title = MEDIA_BASE_SCHEMA_TITLE


class MediaDB(MediaBase):
    """Схема для отображения объекта класса Media в ответе сервера.

    Поля:
        media_url (HttpUrl): ссылка на медиа-файл.
        media_type (str): тип медиа-файла.
        created_at (datetime): дата и время создания.
        updated_at (datetime): Дата и время последнего редактирования.
    """

    created_at: datetime = Field(..., title=CREATED_AT_TITLE)
    updated_at: datetime = Field(..., title=UPDATED_AT_TITLE)

    class Config:
        """Конфигурация Pydantic для схемы MediaDB.

        Поля:
            title: заголовок схемы.
            orm_mode: поле для возможности сериализации объекта
                ORM-модели в Pydantic-схему MediaDB.
        """

        title = MEDIA_DB_SCHEMA_TITLE
        from_attributes = True


class MediaCreate(MediaBase):
    """Схема для создания объекта Media в базе данных.

    Поля:
        media_url (HttpUrl): ссылка на медиа-файл (обязательно).
        media_type (str | None): тип медиа-файла (опционально).
    """

    media_url: HttpUrl = Field(
        ..., min_length=MEDIA_URL_MIN_LENGTH, max_length=MEDIA_URL_MAX_LENGTH
    )

    class Config:
        """Конфигурация Pydantic для схемы MediaCreate.

        Поля:
            title: заголовок схемы.
            schema_extra: задает примеры запросов для Swagger.
        """

        title = MEDIA_CREATE_SCHEMA_TITLE
        schema_extra = {
            'examples': {
                'correct_request': CORRECT_REQUEST,
                'correct_request_without_media_type': (
                    CORRECT_REQUEST_WITHOUT_MEDIA_TYPE
                ),
                'invalid_empty_body_error': (INVALID_EMPTY_BODY_REQUEST),
                'invalid_media_url_format_request': (
                    INVALID_MEDIA_URL_FORMAT_REQUEST
                ),
            }
        }


class MediaUpdate(MediaBase):
    """Схема для обновления объекта Media в базе данных.

    Поля:
        media_url (HttpUrl | None): ссылка на медиа-файл (опционально).
        media_type (str | None): тип медиа-файла (опционально).
    """

    class Config:
        """Конфигурация Pydantic для схемы MediaUpdate.

        Поля:
            title: заголовок схемы.
        """

        title = MEDIA_UPDATE_SCHEMA_TITLE
