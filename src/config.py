import os

from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    app_title: str = os.getenv('APP_TITLE', 'REST API')
    description: str = os.getenv('DESCRIPTION', 'Sales platform')
    db_type: str = os.getenv('DB_TYPE', 'postgresql')
    db_api: str = os.getenv('DB_API', 'asyncpg')
    db_host: str = os.getenv('DB_HOST')
    postgres_user: str = os.getenv('POSTGRES_USER')
    postgres_password: str = os.getenv('POSTGRES_PASSWORD')
    postgres_db: str = os.getenv('POSTGRES_DB')
    port_db_postgres: str = os.getenv('PORT_DB_POSTGRES')
    log_level: str = os.getenv('LOG_LEVEL')
    secret: str = os.getenv('SECRET', 'secret')
    reset_password_token_secret: str = os.getenv('RESET_PASSWORD_SECRET')
    verification_token_secret: str = os.getenv('VERIFICATION_SECRET')
    redis_host: str = os.getenv('REDIS_HOST')
    redis_port: str = os.getenv('REDIS_PORT')
    telegram_token: str = os.getenv('TELEGRAM_BOT_TOKEN')

    @property
    def database_url(self):
        return (
            f'{self.db_type}+{self.db_api}://'
            f'{self.postgres_user}:{self.postgres_password}@'
            f'{self.db_host}:{self.port_db_postgres}'
            f'/{self.postgres_db}'
        )

    model_config = ConfigDict(env_file='.env', extra='ignore')


settings = Settings()
