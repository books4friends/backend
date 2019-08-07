from django.views import View

from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404

from apps.utils.auth import auth_decorator

from ..models import BookItem


class DeleteBookView(View):
    @auth_decorator
    def post(self, request, book_id, *args, **kwargs):
        book_item = get_object_or_404(
            BookItem,
            pk=book_id,
            account_id=self.request.session['account_id']
        )

        book_item.status = BookItem.STATUS.DELETED
        book_item.save(update_fields=['status'])

        return JsonResponse({'success': True, 'book_id': book_item.id})
