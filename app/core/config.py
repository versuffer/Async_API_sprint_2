from pathlib import Path
from typing import Annotated

from pydantic import Extra, Field, HttpUrl, RedisDsn, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

BASEDIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # App
    APP_TITLE: str = 'Async API Sprint 1'
    APP_DESCRIPTION: str = 'Default description'
    DEBUG: bool = False
    LOG_LEVEL: str = 'INFO'

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: str
    REDIS_DSN: RedisDsn | str = ''

    # Elasticsearch
    ELASTIC_HOST: str
    ELASTIC_PORT: str
    ELASTIC_SCHEMA: str
    ELASTIC_URL: HttpUrl | str = ''

    # Cache
    DEFAULT_EXPIRE_TIME_SECONDS: int = 60

    model_config = SettingsConfigDict(env_file=BASEDIR / '.env')

    @field_validator('REDIS_DSN')
    def build_redis_dsn(cls, value: RedisDsn | None, info: ValidationInfo) -> Annotated[str, RedisDsn]:
        if not value:
            value = RedisDsn.build(
                scheme='redis',
                host=info.data['REDIS_HOST'],
                port=info.data['REDIS_PORT'],
                path=f"{info.data['REDIS_DB'] or ''}",
            )
        return str(value)

    @field_validator('ELASTIC_URL')
    def build_elastic_url(cls, value: str | None, info: ValidationInfo) -> HttpUrl:
        if not value:
            value = f'{info.data["ELASTIC_SCHEMA"]}://{info.data["ELASTIC_HOST"]}:{info.data["ELASTIC_PORT"]}'
        return HttpUrl(value)


class ElasticsearchSettings(BaseSettings):
    scheme: str = Field(alias='ELASTIC_SCHEMA')
    host: str = Field(alias='ELASTIC_HOST')
    port: int = Field(alias='ELASTIC_PORT')

    class Config:
        env_file = '.env'
        extra = Extra.ignore


es_settings = ElasticsearchSettings()
app_settings = Settings()
