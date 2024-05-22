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
        "genre_id, expected_status_code",
        [
            (str(uuid.uuid4()), status.HTTP_404_NOT_FOUND),
            ("unknown", status.HTTP_422_UNPROCESSABLE_ENTITY),
            (-8, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ],
    )
    async def test_genre_get_fail(
        self, async_test_client: AsyncClient, es_write_data, es_prepared_data, genre_id, expected_status_code
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

        response = await async_test_client.get(f"/api/v1/genres/{genre_id}")

        assert response.status_code == expected_status_code

    async def test_genre_get_success(
        self, async_test_client: AsyncClient, es_write_data, es_prepared_data, one_genre_data
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
        genre_id = one_genre_data.get('id')
        response = await async_test_client.get(f"/api/v1/genres/{genre_id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json().get('uuid') == genre_id

    async def test_genres_get(
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

        response = await async_test_client.get("/api/v1/genres")

        assert response.status_code == status.HTTP_200_OK
        resp_json = response.json()
        assert len(resp_json) == len(genres_data)
