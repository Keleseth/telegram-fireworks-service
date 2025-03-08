import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import ConfigDict, SecretStr
from pydantic_settings import BaseSettings

env_path = Path(__file__).parent.parent / '.env'  # Поднимаемся на уровень выше
load_dotenv(env_path)
print(f'🔍 Загружаем .env из: {env_path}')


class Settings(BaseSettings):
    app_title: str = os.getenv('APP_TITLE', 'REST API')
    description: str = os.getenv('DESCRIPTION', 'Sales platform')
    db_type: str = os.getenv('DB_TYPE', 'postgresql')
    db_api: str = os.getenv('DB_API', 'asyncpg')
    db_host: str = os.getenv('DB_HOST')
    postgres_user: str = os.getenv('POSTGRES_USER')
    postgres_password: SecretStr = os.getenv('POSTGRES_PASSWORD')
    postgres_db: str = os.getenv('POSTGRES_DB')
    port_bd_postgres: str = os.getenv('PORT_BD_POSTGRES')
    log_level: str = os.getenv('LOG_LEVEL')

    @property
    def database_url(self):
        return (
            f'{self.db_type}+{self.db_api}://'
            f'{self.postgres_user}:{self.postgres_password}@'
            f'{self.db_host}:{self.port_bd_postgres}'
            f'/{self.postgres_db}'
        )

    model_config = ConfigDict(env_file='.env', extra='ignore')


settings = Settings()
