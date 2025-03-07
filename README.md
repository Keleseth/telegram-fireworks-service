# Joker Fireworks - телеграм бот + Fast API приложение по продаже пиротехники

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Python-Telegram-Bot](https://img.shields.io/badge/python--telegram--bot-%2300A1E0.svg?style=for-the-badge&logo=telegram&logoColor=white) ![Bitrix24](https://img.shields.io/badge/bitrix24-%2323A3F3.svg?style=for-the-badge&logo=bitrix24&logoColor=white) ![FastAPI](https://img.shields.io/badge/fastapi-%2300C7B7.svg?style=for-the-badge&logo=fastapi&logoColor=white) ![FastAPI Users](https://img.shields.io/badge/fastapi--users-%2300C7B7.svg?style=for-the-badge&logo=fastapi&logoColor=white) ![Uvicorn](https://img.shields.io/badge/uvicorn-%23007ACC.svg?style=for-the-badge&logo=python&logoColor=white) ![Pydantic](https://img.shields.io/badge/pydantic-%2300A1E0.svg?style=for-the-badge&logo=python&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%23F47216.svg?style=for-the-badge&logo=python&logoColor=white) ![Alembic](https://img.shields.io/badge/alembic-%230071C5.svg?style=for-the-badge&logo=alembic&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/postgresql-%23336791.svg?style=for-the-badge&logo=postgresql&logoColor=white) ![Swagger](https://img.shields.io/badge/swagger-%2385EA2D.svg?style=for-the-badge&logo=swagger&logoColor=black) ![ReDoc](https://img.shields.io/badge/redoc-%23CB3837.svg?style=for-the-badge&logo=redoc&logoColor=white)

# Шаблон для проектов со стилизатором Ruff

## Основное

1. Базовая версия Python "^3.12"
2. В файле `requirements_style.txt` находятся зависимости для стилистики.
3. В каталоге `src` находится базовая структура проекта
4. В файле `srd/requirements.txt` прописываются базовые зависимости.
5. В каталоге `infra` находятся настроечные файлы проекта. Здесь же размещать файлы для docker compose.

### Важно!
- Все задачи, исправления, багфиксы выполняем создавая соответствующую ветку от ветки develop предварительно сделав git pull ветки dev. После выполнения задачи, а лучше во время выполнения задачи заводим pull request ветки фичи/багфикса -> в ветку dev. Чаще лучше сделать pull request заарнее, чтобы было видно направление куда двигаемся, все последующие push будут добавляться к текущему pull request, так что это не проблема.
- Именование веток:
  - для задачи `feature/задача`
  - для багфикса `bugfix/что за багфикс`

### Начало работы
- клонировать репозиторий
- создать и активировать виртуальное окружение, обновить пип, установить зависимости из файла src/requirements.txt и файла requirements_style.txt
- по .env.example из папки infra сделать .env файл в ту же папку infra, и можно запускать `docker compose -f infra/docker-compose.local.yaml up -d` из папки проекта

## Стилистика

Для стилизации кода используется пакеты `Ruff` и `Pre-commit`

Проверка стилистики кода осуществляется командой
```shell
ruff check
```

Если одновременно надо пофиксить то, что можно поиксить автоматически, то добавляем параметр `--fix`
```shell
ruff check --fix
```

Что бы стилистика автоматически проверялась и поправлялась при комитах надо добавить hook pre-commit к git

```shell
pre-commit install
```

после выполнения команды `pre-commit install` git будет автоматически проверять код перед каждым коммитом и вносить изменения там, где он может это делать автоматически. Файл с настройками .pre-commit-config.yaml
