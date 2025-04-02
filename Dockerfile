FROM python:3.12-slim

WORKDIR /app

# Устанавливаем curl и зависимости для psycopg2
RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*


# Копируем requirements.txt из папки src
COPY src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#Копируем остальные файлы
COPY .env .
COPY .env src/service/
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY scripts/ ./scripts/
COPY src/ ./src/
COPY statics/ ./static/


ENV PYTHONPATH=/app
# Команда запуска указана в docker-compose для поддержки --reload

