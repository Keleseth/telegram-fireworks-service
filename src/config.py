import os

from dotenv import load_dotenv
from pydantic import ConfigDict, SecretStr
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    app_title: str = os.getenv('APP_TITLE', 'REST API')
    description: str = os.getenv('DESCRIPTION', 'Sales platform')
    db_type: str = os.getenv('DB_TYPE', 'postgresql')
    db_api: str = os.getenv('DB_API', 'asyncpg')
    db_host: str = os.getenv('DB_HOST')
    postgres_user: str = os.getenv('POSTGRES_USER')
    postgres_password: SecretStr = os.getenv('POSTGRES_PASSWORD')
    postgres_db: str = os.getenv('POSTGRES_DB')
    port_db_postgres: str = os.getenv('PORT_DB_POSTGRES')
    log_level: str = os.getenv('LOG_LEVEL')

    @property
    def database_url(self):
        return os.getenv('DATABASE_URL')

    model_config = ConfigDict(env_file='.env', extra='ignore')


settings = Settings()
