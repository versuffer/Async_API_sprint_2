import json

import pytest
from httpx import AsyncClient

from tests.functional.testdata.movie_data import es_movie_index_mapping, movie_data
from tests.functional.testdata.person_data import es_persons_index, persons_from_film

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
        self,
        async_test_client: AsyncClient,
        es_write_data,
        es_prepared_data,
        es_clear_index,
        query_data: dict,
        expected_answer: dict,
    ):
        es_clear_index(es_index=self.PERSON_INDEX, index_mapping=es_persons_index)
        es_clear_index(es_index=self.MOVIE_INDEX, index_mapping=es_movie_index_mapping)

        es_write_data(
            es_index=self.PERSON_INDEX,
            index_mapping=es_persons_index,
            data=es_prepared_data(index=self.PERSON_INDEX, data=persons_from_film),
        )

        response = await async_test_client.get('/api/v1/persons/search', params=query_data)

        assert response.status_code == expected_answer['status']
        assert len(response.json()) == expected_answer['length']

    @pytest.mark.parametrize(
        'person_data, expected_answer',
        [
            ({'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95'}, {'status': 200}),
            ({'id': 'ae45bcf2-17a4-4db1-aa55-b5e5b051e87e'}, {'status': 404}),
        ],
    )
    async def test_person_detail(
        self,
        async_test_client: AsyncClient,
        es_write_data,
        es_prepared_data,
        es_clear_index,
        person_data: dict,
        expected_answer: dict,
    ):
        es_clear_index(es_index=self.PERSON_INDEX, index_mapping=es_persons_index)
        es_clear_index(es_index=self.MOVIE_INDEX, index_mapping=es_movie_index_mapping)

        es_write_data(
            es_index=self.PERSON_INDEX,
            index_mapping=es_persons_index,
            data=es_prepared_data(index=self.PERSON_INDEX, data=persons_from_film),
        )

        response = await async_test_client.get(f'/api/v1/persons/{person_data["id"]}', params=person_data)

        assert response.status_code == expected_answer['status']

    @pytest.mark.parametrize(
        'person_data, expected_answer',
        [
            ({'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95'}, {'status': 200, 'person_films': 10}),
            ({'id': 'ae45bcf2-17a4-4db1-aa55-b5e5b051e87e'}, {'status': 200, 'person_films': 0}),
        ],
    )
    async def test_person_film(
        self,
        async_test_client: AsyncClient,
        es_delete_data,
        es_write_data,
        es_prepared_data,
        es_clear_index,
        person_data: dict,
        expected_answer: dict,
    ):

        es_clear_index(es_index=self.PERSON_INDEX, index_mapping=es_persons_index)
        es_clear_index(es_index=self.MOVIE_INDEX, index_mapping=es_movie_index_mapping)

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

        response = await async_test_client.get(f'/api/v1/persons/{person_data["id"]}/film', params=person_data)

        assert response.status_code == expected_answer['status']
        assert len(response.json()) == expected_answer['person_films']

    async def test_cache_person_detail(
        self,
        async_test_client: AsyncClient,
        es_write_data,
        es_prepared_data,
        es_delete_data,
        redis_client,
        es_clear_index,
    ):

        person_data = {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95'}

        await redis_client.flushall()

        es_clear_index(es_index=self.PERSON_INDEX, index_mapping=es_persons_index)
        es_clear_index(es_index=self.MOVIE_INDEX, index_mapping=es_movie_index_mapping)

        es_write_data(
            es_index=self.PERSON_INDEX,
            index_mapping=es_persons_index,
            data=es_prepared_data(index=self.PERSON_INDEX, data=persons_from_film),
        )

        response_before_del = await async_test_client.get(f'/api/v1/persons/{person_data["id"]}', params=person_data)
        assert response_before_del.status_code == 200

        es_delete_data(es_index=self.PERSON_INDEX, obj_id=person_data['id'])

        redis_keys = await redis_client.keys("fastapi-cache:*")
        assert len(redis_keys) == 1

        get_redis_key = await redis_client.get(redis_keys[0])
        assert json.loads(get_redis_key).get('id') == response_before_del.json().get('uuid')

        await redis_client.flushall()

        redis_keys_after_del = await redis_client.keys("fastapi-cache:*")
        assert len(redis_keys_after_del) == 0

        response_after_teardown_redis = await async_test_client.get(
            f'/api/v1/persons/{person_data["id"]}', params=person_data
        )
        assert response_after_teardown_redis.status_code == 404
