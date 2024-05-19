import uuid
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from httpx import AsyncClient

from tests.functional.settings import test_settings


#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий.

pytestmark = pytest.mark.anyio


async def test_search(async_test_client: AsyncClient):
    # 1. Генерируем данные для ES
    es_data = [{
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
            {'id': 'caf76c67-c0fe-477e-8a66-3ab3ff2574b5', 'name': 'Stan'}
        ]
    } for _ in range(18)]

    bulk_query: list[dict] = []
    for row in es_data:
        data = {'_index': 'movies', '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    # 2. Загружаем данные в ES
    es_client = AsyncElasticsearch(hosts=test_settings.es_host, verify_certs=False)
    if await es_client.indices.exists(index=test_settings.es_index):
        await es_client.indices.delete(index=test_settings.es_index)
    await es_client.indices.create(index=test_settings.es_index, **test_settings.es_index_mapping)

    updated, errors = await async_bulk(client=es_client, actions=bulk_query)

    await es_client.close()

    if errors:
        raise Exception('Ошибка записи данных в Elasticsearch')

    # 3. Запрашиваем данные из ES по API
    query_data = {'search_query': 'Star', 'page': 1, 'page_size': 20}
    response = await async_test_client.get('/api/v1/films/search', params=query_data)

    # 4. Проверяем ответ 

    assert response.status_code == 200
    assert len(response.json()) == 20
