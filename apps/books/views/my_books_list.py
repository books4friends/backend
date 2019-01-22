from django.http.response import JsonResponse
from django.views import View

from apps.utils.auth import auth_decorator

from ..models import BookItem


class MyBooksList(View):
    @auth_decorator
    def get(self, request, *args, **kwargs):
        account_id = request.session.get('account_id')
        books = BookItem.objects.filter(
            account_id=account_id,
            status__in=[BookItem.STATUS.ACTIVE, BookItem.STATUS.NOT_ACTIVE],
        ).order_by('-pk').select_related('detail')
        books_json = [{
            "id": str(book.pk),
            "description":{
                "title": book.detail.title,
                "author": book.detail.author,
                "image": book.detail.image_external_url
            },
            "comment": book.comment,
            "active": book.status == BookItem.STATUS.ACTIVE,

        } for book in books]
        return JsonResponse({"books": books_json})
