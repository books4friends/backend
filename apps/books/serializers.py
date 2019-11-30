from .models import Book


class BookSerializer:
    @classmethod
    def serialize(cls, obj):
        if isinstance(obj, Book):
            return cls._serialize_one(obj)
        else:
            return cls._serialize_list(obj)

    @classmethod
    def _serialize_one(cls, book):
        if book.image.name:
            image = book.image.url
        elif book.image_external_url:
            image = book.image_external_url
        else:
            image = None

        return {
            "id": str(book.pk),
            "description": {
                "title": book.title,
                "author": book.author,
                "description": book.description,
                "genre": int(book.genre) if book.genre else None,
                "image": image,
            },
            "comment": book.comment,
            "active": book.status == Book.STATUS.ACTIVE,
        }

    @classmethod
    def _serialize_list(cls, books):
        return [cls._serialize_one(book) for book in books]
