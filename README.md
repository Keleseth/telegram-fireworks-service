# Fireworks Shop Bot — Telegram-бот и FastAPI API для продажи пиротехники

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/fastapi-%2300C7B7.svg?style=for-the-badge&logo=fastapi&logoColor=white)
![Telegram Bot](https://img.shields.io/badge/python--telegram--bot-%2300A1E0.svg?style=for-the-badge&logo=telegram&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgresql-%23336791.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![NGINX](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%23F47216.svg?style=for-the-badge&logo=python&logoColor=white)
![Alembic](https://img.shields.io/badge/alembic-%230071C5.svg?style=for-the-badge&logo=alembic&logoColor=white)
![APScheduler](https://img.shields.io/badge/apscheduler-%2300A1E0.svg?style=for-the-badge&logo=python&logoColor=white)
![SQLAdmin](https://img.shields.io/badge/sqladmin-%2300C7B7.svg?style=for-the-badge&logo=fastapi&logoColor=white)

---

## Описание проекта

Проект разработан по заказу поставщика пиротехники для автоматизации розничного оформления заказов через Telegram-бота.
Цель — предоставить пользователям простой способ выбора и покупки фейерверков, а администраторам — удобные инструменты для управления товарами и рассылками.
Доступ к заказам лицам старше 18 лет.
В проекте реализован backend на FastAPI, отвечающий только за обработку запросов от бота через API, проходящих по локальному адресу сервера.

Основной функционал:
- Просмотр товаров, фильтрация по категориям, тегам, ценам и прочим характеристикам.
- Оформление и отслеживание заказов через Telegram-бота.
- Отправка рассылок пользователям с помощью APScheduler. Реализована фильтрация списка получателей по разнообразным критериям.
- Администрирование базы данных через панель управления на базе SQLAdmin.
- Асинхронная работа сервиса с использованием FastAPI и SQLAlchemy.

## Начало работы

### Деплой проекта на сервер
Деплой настроен через GitHub Actions. При пуше в ветки develop, master, feature/develop происходит автоматическая сборка образов и их доставка на сервер.

Требования для корректной работы:
- на сервере установлен Docker и Docker Compose
- на сервере создана папка проекта /opt/fireworks_shop_bot/
- в этой папке должен находиться .env файл, созданный на основе infra/.env.example
- Убедитесь, что в .env указан ваш токен Telegram-бота (BOT_TOKEN).
- в репозитории настроены секреты:
  - HOST — IP-адрес сервера
  - USER — SSH-пользователь
  - SSH_KEY — приватный ключ
  - SSH_PASSPHRASE — пароль к ключу (если есть)
  - DOCKER_USERNAME и DOCKER_PASSWORD — данные для Docker Hub

Процесс деплоя:

после коммита в указанные ветки GitHub Actions:

собирает образы приложения, бота и nginx

пушит их на Docker Hub

подключается к серверу по SSH

копирует docker-compose.yaml на сервер

выполняет команды:

### Локальный запуск проекта (только для целей разработки)
⚠️ В проекте используется nginx для проброса запросов и Webhook для работы Telegram-бота.
Для полноценной работы проекта требуется внешний IP-адрес.
Локальный запуск возможен только после следующих изменений:
- В коде необходимо заменить все обращения к nginx:8000 на 127.0.0.1:8000.
- Перевести Telegram-бот на режим Polling вместо Webhook:
  - перейти в файл src/bot/main.py, закомментировать блок кода run_webhook, раскомментировать блок кода polling.

Шаги для локальной разработки:
1. Установка python версии 3.12+
2. Клонируйте репозиторий
```bash
- git clone https://github.com/your_username/fireworks-shop-bot.git
```
перейдите в созданный локальный репозиторий.

3. Создайте и активируйте виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
```

4. Обновите pip если требуется.
```  bash
pip install --upgrade pip
```

5. Установите зависимости
``` bash
pip install -r src/requirements.txt
pip install -r requirements_style.txt # для разработки
```

6. Создайте .env файл:
- На основе файла infra/.env.example создайте там же .env
- Заполните его необходимыми данными

7. Запустите проект через Docker Compose
(docker должен быть запущен).
```bash
docker compose -f infra/docker-compose.local.yaml up -d
```

### Дополнительная информация
Документация API доступна после запуска сервера по адресу:
- `http://localhost:8000/docs` — Swagger UI
- `http://localhost:8000/redoc` — Redoc UI


### Проект разработан командой из 6 разработчиков:
- Тимлид Келесидис Александр [Keleseth](https://github.com/Keleseth)
- Разработчик Константин Походяев [KonstantinPohodyaev](https://github.com/KonstantinPohodyaev)
- Разработчик Евгений Лепёха [Evgn22](https://github.com/Evgn22)
- Разработчик Сергей Варюхов [s1zeist](https://github.com/s1zeist)
- Разработчик Савва Великородов [OoopsDope](https://github.com/OoopsDope)
- Разработчик Степан Герасимов [Stepan22042004](https://github.com/Stepan22042004)
- Разработчик Вадим Пронькин [mrvadzzz](https://github.com/mrvadzzz)
