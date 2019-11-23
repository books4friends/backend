from django.http.response import JsonResponse
from django.views import View

from apps.utils.auth import auth_decorator

from ..serializers import BookSerializer

from ..models import Book


class MyBooksList(View):
    @auth_decorator
    def get(self, request, *args, **kwargs):
        account_id = request.session.get('account_id')
        books = Book.objects.filter(
            account_id=account_id,
            status__in=[Book.STATUS.ACTIVE, Book.STATUS.NOT_ACTIVE],
        ).order_by('-pk')
        books_json = BookSerializer.serialize(books)
        return JsonResponse({"books": books_json})
