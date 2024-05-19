from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    TEST_ES_HOST: str
    TEST_REDIS_HOST: str


test_settings = TestSettings()
