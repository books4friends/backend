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
        if book.detail.image.name:
            image = book.detail.image.url
        elif book.detail.image_external_url:
            image = book.detail.image_external_url
        else:
            image = None

        return {
            "id": str(book.pk),
            "description":{
                "title": book.detail.title,
                "author": book.detail.author,
                "image": image,
            },
            "comment": book.comment,
            "active": book.status == BookItem.STATUS.ACTIVE,

        }

    @classmethod
    def _serialize_list(cls, books):
        return [cls._serialize_one(book) for book in books]
