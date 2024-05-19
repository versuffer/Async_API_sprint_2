import pytest
from httpx import AsyncClient

from tests.functional.testdata.movie_data import es_persons_index, person_data

pytestmark = pytest.mark.anyio


class TestPersons:

    INDEX: str = 'persons'

    @pytest.mark.parametrize(
        'query_data, expected_answer',
        [
            ({'search_query': 'Team', 'page': 1, 'page_size': 20}, {'status': 200, 'length': 10}),
            ({'search_query': 'Mashed potato'}, {'status': 200, 'length': 0}),
        ],
    )
    async def test_person_search(
        self, async_test_client: AsyncClient, es_write_data, es_prepared_data, query_data: dict, expected_answer: dict
    ):

        es_write_data(
            es_index=self.INDEX,
            index_mapping=es_persons_index,
            data=es_prepared_data(index=self.INDEX, data=person_data),
        )

        response = await async_test_client.get('/api/v1/persons/search', params=query_data)

        assert response.status_code == expected_answer['status']
        assert len(response.json()) == expected_answer['length']
