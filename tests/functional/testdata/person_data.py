es_persons_index = {
    "settings": {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {"type": "stop", "stopwords": "_english_"},
                "english_stemmer": {"type": "stemmer", "language": "english"},
                "english_possessive_stemmer": {"type": "stemmer", "language": "possessive_english"},
                "russian_stop": {"type": "stop", "stopwords": "_russian_"},
                "russian_stemmer": {"type": "stemmer", "language": "russian"},
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer",
                    ],
                }
            },
        },
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {"type": "keyword"},
            "full_name": {"type": "text", "analyzer": "ru_en", "fields": {"raw": {"type": "keyword"}}},
        },
    },
}

persons_from_film = [
    {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'full_name': 'Ann'},
    {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'full_name': 'Bob'},
    {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'full_name': 'Ben'},
    {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'full_name': 'Howard'},
    {'id': '5d33e65b-948c-4d73-a037-2779a105dd75', 'full_name': 'Stan'},
]
