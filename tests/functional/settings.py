from pydantic import Field
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    es_host: str = 'http://localhost:9200'
    es_index: str = "movies"
    # es_id_field: str = ...

    redis_host: str = 'http://127.0.0.1:6379'
    service_url: str = 'http://127.0.0.1'


test_settings = TestSettings()
