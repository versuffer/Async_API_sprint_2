from typing import AsyncGenerator

import pytest
import redis.asyncio as redis
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from httpx import AsyncClient

from app.main import app as fastapi_app
from tests.functional.settings import test_settings
from tests.functional.testdata.genres_data import genre_action
from tests.functional.testdata.movie_data import cool_movie


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope='session')
async def redis_client():
    client = redis.Redis.from_url(test_settings.REDIS_DSN, decode_responses=True)
    try:
        await client.ping()
        print("Successfully connected to Redis")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
    yield client
    await client.close()


# @pytest.fixture
# async def teardown_redis(radis_client: Redis):
#     yield
#     radis_client.flushall()


@pytest.fixture
async def async_test_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=fastapi_app, base_url='http://test') as app:
        yield app


@pytest.fixture(scope='session')
async def es_client() -> AsyncGenerator[Elasticsearch, Elasticsearch]:
    es_client = Elasticsearch(
        hosts=[test_settings.ELASTIC_URL],
        verify_certs=False,
    )
    yield es_client
    es_client.close()


@pytest.fixture
def es_delete_data(es_client: Elasticsearch):
    def inner(es_index: str, obj_id: str):
        es_client.delete(index=es_index, id=obj_id, refresh=True)

    return inner


@pytest.fixture
def es_write_data(es_client: Elasticsearch):
    def inner(es_index: str, index_mapping: dict, data: list[dict]):
        if es_client.indices.exists(index=es_index):
            es_client.indices.delete(index=es_index)
        es_client.indices.create(index=es_index, **index_mapping)

        updated, errors = bulk(client=es_client, actions=data, refresh=True)

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest.fixture
def es_clear_index(es_client: Elasticsearch):
    def inner(es_index: str, index_mapping: dict):
        if es_client.indices.exists(index=es_index):
            es_client.indices.delete(index=es_index)
        es_client.indices.create(index=es_index, **index_mapping)

    return inner


@pytest.fixture
def es_prepared_data():
    def inner(index: str, data: list[dict]):

        bulk_query: list[dict] = []
        for row in data:
            bulk_data = {'_index': index, '_id': row['id']}
            bulk_data.update({'_source': row})
            bulk_query.append(bulk_data)

        return bulk_query

    return inner


@pytest.fixture
def one_movie_data():
    return cool_movie


@pytest.fixture
def one_genre_data():
    return genre_action
