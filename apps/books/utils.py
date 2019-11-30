from django.utils import translation
from .models import Book


def get_genres_list():
    genres = \
        [
            {
                "index": index,
                "slug": genre,
                "title": translation.gettext('genre_' + genre)
            }
            for index, genre in enumerate(Book.GENRES)
        ]
    genres.sort(key=lambda x: x['title'])
    return genres