import uuid


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
