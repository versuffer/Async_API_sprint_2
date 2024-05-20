from uuid import UUID

import pytest
from httpx import AsyncClient

from tests.functional.testdata.movie_data import es_movie_index_mapping, movie_data
from tests.functional.testdata.person_data import es_persons_index, persons_from_film
from app.main import app as fastapi_app
pytestmark = pytest.mark.anyio


class TestPersons:

    MOVIE_INDEX: str = 'movies'
    PERSON_INDEX: str = 'persons'

    @pytest.mark.parametrize(
        'query_data, expected_answer',
        [
            ({'search_query': 'Ann', 'page': 1, 'page_size': 20}, {'status': 200, 'length': 1}),
            ({'search_query': 'Mashed potato'}, {'status': 200, 'length': 0}),
        ],
    )
    async def test_person_search(
        self, async_test_client: AsyncClient, es_write_data, es_prepared_data, query_data: dict, expected_answer: dict
    ):

        es_write_data(
            es_index=self.PERSON_INDEX,
            index_mapping=es_persons_index,
            data=es_prepared_data(index=self.PERSON_INDEX, data=persons_from_film),
        )

        response = await async_test_client.get('/api/v1/persons/search', params=query_data)

        assert response.status_code == expected_answer['status']
        assert len(response.json()) == expected_answer['length']

    async def test_person_detail(self, async_test_client: AsyncClient, es_write_data, es_prepared_data):

        es_write_data(
            es_index=self.PERSON_INDEX,
            index_mapping=es_persons_index,
            data=es_prepared_data(index=self.PERSON_INDEX, data=persons_from_film),
        )

        es_write_data(
            es_index=self.MOVIE_INDEX,
            index_mapping=es_movie_index_mapping,
            data=es_prepared_data(index=self.MOVIE_INDEX, data=movie_data),
        )

        person_id = persons_from_film[0].get('id')
        response = await async_test_client.get(fastapi_app.url_path_for('get_person', person_id=person_id))

        assert response.status_code == 200
        assert len(response.json()) == 1