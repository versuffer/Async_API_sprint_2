from functools import wraps
from typing import AsyncGenerator
from unittest import mock

import pytest
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from httpx import AsyncClient

from tests.functional.settings import test_settings


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope='session')
async def async_test_client() -> AsyncGenerator[AsyncClient, None]:
    from app.main import app as fastapi_app

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
    def inner(es_index: str, data_id: str):
        es_client.delete(index=es_index, id=data_id, refresh=True)

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
def es_prepared_data():
    def inner(index: str, data: list[dict]):

        bulk_query: list[dict] = []
        for row in data:
            bulk_data = {'_index': index, '_id': row['id']}
            bulk_data.update({'_source': row})
            bulk_query.append(bulk_data)

        return bulk_query

    return inner
