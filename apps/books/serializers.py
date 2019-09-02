from .models import BookItem


class BookItemSerializer:
    @classmethod
    def serialize(cls, obj):
        if isinstance(obj, BookItem):
            return cls._serialize_one(obj)
        else:
            return cls._serialize_list(obj)

    @classmethod
    def _serialize_one(cls, book):
        return {
            "id": str(book.pk),
            "description":{
                "title": book.detail.title,
                "author": book.detail.author,
                "image": book.detail.image.url if book.detail.image.name else None,
            },
            "comment": book.comment,
            "active": book.status == BookItem.STATUS.ACTIVE,

        }

    @classmethod
    def _serialize_list(cls, books):
        return [cls._serialize_one(book) for book in books]
