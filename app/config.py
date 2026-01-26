from logging import getLevelNamesMapping
from typing import Literal

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggerConfig(BaseModel):
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'

    @property
    def log_level(self) -> int:
        return getLevelNamesMapping()[self.level]


class BotConfig(BaseModel):
    token: SecretStr


class AppConfig(BaseModel):
    url: SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix='APP__',
        env_nested_delimiter='__',
        env_file='.env',
        env_file_encoding='utf-8',
        env_ignore_empty=True,
    )

    logger: LoggerConfig = LoggerConfig()
    bot: BotConfig
    app: AppConfig


settings = Settings.model_validate({})
