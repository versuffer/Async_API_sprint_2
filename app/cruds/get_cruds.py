from app.cruds.elastic import FilmElasticCrud, GenreElasticCrud, PersonElasticCrud


def get_film_crud():
    return FilmElasticCrud()


def get_genre_crud():
    return GenreElasticCrud()


def get_person_crud():
    return PersonElasticCrud()
