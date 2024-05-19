import uuid
from typing import AsyncGenerator

from elasticsearch import Elasticsearch

from app.main import app as fastapi_app
import pytest
from httpx import AsyncClient

from tests.functional.settings import test_settings
from elasticsearch.helpers import async_bulk, streaming_bulk
from elasticsearch.helpers import bulk


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture
async def async_test_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=fastapi_app, base_url='http://test') as app:
        yield app


@pytest.fixture(name='es_client', scope='session')
async def es_client() -> Elasticsearch:
    es_client = Elasticsearch(hosts=test_settings.es_host, verify_certs=False)
    yield es_client
    es_client.close()


@pytest.fixture(name='es_write_data')
def es_write_data(es_client: Elasticsearch):
    def inner(data: list[dict]):
        if es_client.indices.exists(index=test_settings.es_index):
            es_client.indices.delete(index=test_settings.es_index)
        es_client.indices.create(index=test_settings.es_index, **test_settings.es_index_mapping)

        updated, errors = bulk(client=es_client, actions=data)

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


@pytest.fixture(name='es_movie_data')
def es_movie_data():

    movie_data = [{
            'id': str(uuid.uuid4()),
            'imdb_rating': 8.5,
            'genres': ['Action', 'Sci-Fi'],
            'title': 'The Star',
            'description': 'New World',
            'directors_names': ['Stan'],
            'actors_names': ['Ann', 'Bob'],
            'writers_names': ['Ben', 'Howard'],
            'actors': [
                {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
                {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
            ],
            'writers': [
                {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
                {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'}
            ],
            'directors': [
                {'id': '5d33e65b-948c-4d73-a037-2779a105dd75', 'name': 'Stan'}
            ]
        } for _ in range(10)]

    bulk_query: list[dict] = []
    for row in movie_data:
        data = {'_index': 'movies', '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    return bulk_query