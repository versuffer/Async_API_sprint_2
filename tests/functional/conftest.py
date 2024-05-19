import uuid
from pprint import pprint
from time import sleep
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from elasticsearch import Elasticsearch
from elasticsearch.helpers import async_bulk, bulk, streaming_bulk
from httpx import AsyncClient

from app.main import app as fastapi_app
from tests.functional.settings import test_settings
from tests.functional.testdata.movie_data import movie_data


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture
async def async_test_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=fastapi_app, base_url='http://test') as app:
        yield app


@pytest.fixture(scope='session')
async def es_client() -> Elasticsearch:
    es_client = Elasticsearch(hosts=test_settings.ES_HOST, verify_certs=False)
    yield es_client
    es_client.close()


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
def es_prepared_data():
    def inner(index: str, data: list[dict]):

        bulk_query: list[dict] = []
        for row in data:
            data = {'_index': index, '_id': row['id']}
            data.update({'_source': row})
            bulk_query.append(data)

        return bulk_query

    return inner
