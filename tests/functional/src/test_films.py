import uuid

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.functional.testdata.genres_data import es_genres_index_mapping, genres_data
from tests.functional.testdata.movie_data import es_movie_index_mapping, movie_data

pytestmark = pytest.mark.anyio


class TestFilms:
    MOVIE_INDEX: str = 'movies'
    GENRE_INDEX: str = 'genres'

    @pytest.mark.parametrize(
        'query_data, expected_answer',
        [
            ({'search_query': 'Star', 'page': 1, 'page_size': 20}, {'status': status.HTTP_200_OK, 'length': 10}),
            ({'search_query': 'Mashed potato'}, {'status': status.HTTP_200_OK, 'length': 0}),
        ],
    )
    async def test_films_search(
        self, async_test_client: AsyncClient, es_write_data, es_prepared_data, query_data: dict, expected_answer: dict
    ):

        es_write_data(
            es_index=self.MOVIE_INDEX,
            index_mapping=es_movie_index_mapping,
            data=es_prepared_data(index=self.MOVIE_INDEX, data=movie_data),
        )

        response = await async_test_client.get('/api/v1/films/search', params=query_data)

        assert response.status_code == expected_answer['status']
        assert len(response.json()) == expected_answer['length']

    @pytest.mark.parametrize(
        "movie_id, expected_status_code",
        [
            (str(uuid.uuid4()), status.HTTP_404_NOT_FOUND),
            ("unknown", status.HTTP_422_UNPROCESSABLE_ENTITY),
            (-8, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ],
    )
    async def test_film_get_fail(
        self, async_test_client: AsyncClient, es_write_data, es_prepared_data, movie_id, expected_status_code
    ):
        es_write_data(
            es_index=self.MOVIE_INDEX,
            index_mapping=es_movie_index_mapping,
            data=es_prepared_data(index=self.MOVIE_INDEX, data=movie_data),
        )

        es_write_data(
            es_index=self.GENRE_INDEX,
            index_mapping=es_genres_index_mapping,
            data=es_prepared_data(index=self.GENRE_INDEX, data=genres_data),
        )

        response = await async_test_client.get(f"/api/v1/films/{movie_id}")

        assert response.status_code == expected_status_code

    async def test_film_get_success(
        self, async_test_client: AsyncClient, es_write_data, es_prepared_data, one_movie_data
    ):
        es_write_data(
            es_index=self.MOVIE_INDEX,
            index_mapping=es_movie_index_mapping,
            data=es_prepared_data(index=self.MOVIE_INDEX, data=movie_data),
        )

        es_write_data(
            es_index=self.GENRE_INDEX,
            index_mapping=es_genres_index_mapping,
            data=es_prepared_data(index=self.GENRE_INDEX, data=genres_data),
        )
        movie_id = one_movie_data.get('id')
        response = await async_test_client.get(f"/api/v1/films/{movie_id}")

        assert response.status_code == status.HTTP_200_OK
        resp_json = response.json()
        assert resp_json.get('uuid') == movie_id

    async def test_films_get(
        self,
        async_test_client: AsyncClient,
        es_write_data,
        es_prepared_data,
    ):
        es_write_data(
            es_index=self.MOVIE_INDEX,
            index_mapping=es_movie_index_mapping,
            data=es_prepared_data(index=self.MOVIE_INDEX, data=movie_data),
        )

        es_write_data(
            es_index=self.GENRE_INDEX,
            index_mapping=es_genres_index_mapping,
            data=es_prepared_data(index=self.GENRE_INDEX, data=genres_data),
        )

        response = await async_test_client.get("/api/v1/films")

        assert response.status_code == status.HTTP_200_OK
        resp_json = response.json()
        assert len(resp_json) == len(movie_data)
        assert resp_json[0].get('imdb_rating') == 0.0

    async def test_films_get_sort(
        self,
        async_test_client: AsyncClient,
        es_write_data,
        es_prepared_data,
    ):
        es_write_data(
            es_index=self.MOVIE_INDEX,
            index_mapping=es_movie_index_mapping,
            data=es_prepared_data(index=self.MOVIE_INDEX, data=movie_data),
        )

        es_write_data(
            es_index=self.GENRE_INDEX,
            index_mapping=es_genres_index_mapping,
            data=es_prepared_data(index=self.GENRE_INDEX, data=genres_data),
        )

        response = await async_test_client.get("/api/v1/films", params={'sort': '-imdb_rating'})

        assert response.status_code == status.HTTP_200_OK
        resp_json = response.json()
        assert len(resp_json) == len(movie_data)
        assert resp_json[0].get('imdb_rating') == 9.0
        assert resp_json[-1].get('imdb_rating') == 0.0

    async def test_films_get_genre(
        self, async_test_client: AsyncClient, es_write_data, es_prepared_data, one_genre_data, one_movie_data
    ):
        es_write_data(
            es_index=self.MOVIE_INDEX,
            index_mapping=es_movie_index_mapping,
            data=es_prepared_data(index=self.MOVIE_INDEX, data=movie_data),
        )

        es_write_data(
            es_index=self.GENRE_INDEX,
            index_mapping=es_genres_index_mapping,
            data=es_prepared_data(index=self.GENRE_INDEX, data=genres_data),
        )

        response = await async_test_client.get("/api/v1/films", params={'genre': one_genre_data.get('id')})

        assert response.status_code == status.HTTP_200_OK
        resp_json = response.json()
        assert len(resp_json) == 1
        assert resp_json[0].get('uuid') == one_movie_data.get('id')
