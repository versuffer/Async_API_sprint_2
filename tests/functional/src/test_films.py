import uuid
from time import sleep

import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from httpx import AsyncClient

from tests.functional.settings import test_settings
from tests.functional.testdata.movie_data import es_movie_index_mapping, movie_data

pytestmark = pytest.mark.anyio


class TestFilms:

    INDEX: str = 'movies'

    @pytest.mark.parametrize(
        'query_data, expected_answer',
        [
            ({'search_query': 'Star', 'page': 1, 'page_size': 20}, {'status': 200, 'length': 10}),
            ({'search_query': 'Mashed potato'}, {'status': 200, 'length': 0}),
        ],
    )
    async def test_films_search(
        self, async_test_client: AsyncClient, es_write_data, es_prepared_data, query_data: dict, expected_answer: dict
    ):

        es_write_data(
            es_index=self.INDEX,
            index_mapping=es_movie_index_mapping,
            data=es_prepared_data(index=self.INDEX, data=movie_data),
        )

        response = await async_test_client.get('/api/v1/films/search', params=query_data)

        assert response.status_code == expected_answer['status']
        assert len(response.json()) == expected_answer['length']

    # async def test_person_search(self, async_test_client: AsyncClient, es_write_data, es_movie_data: list[dict],
    #                             query_data: dict, expected_answer: dict):
    #
    #     es_write_data(es_movie_data)
    #     response = await async_test_client.get('/api/v1/films/search', params=query_data)
    #
    #     assert response.status_code == expected_answer['status']
    #     assert len(response.json()) == expected_answer['length']
