from django.views import View

import json

from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404

from apps.utils.auth import auth_decorator

from ..models import BookItem
from ..forms import EditBookItemCommentForm


class EditBookItemCommentView(View):
    @auth_decorator
    def post(self, request, book_id, *args, **kwargs):
        book_item = get_object_or_404(
            BookItem,
            pk=book_id,
            account_id=self.request.session['account_id'],
            status__in=[BookItem.STATUS.NOT_ACTIVE, BookItem.STATUS.ACTIVE]
        )

        data = json.loads(request.body.decode('utf-8'))
        form = EditBookItemCommentForm(data)
        if form.is_valid():
            book_item.comment = form.cleaned_data['comment']
            book_item.save(update_fields=['comment'])
            return JsonResponse({'success': True, 'book_id': book_item.id})
        else:
            return JsonResponse({'success': False, 'book_id': book_item.id})


class ActivateBookItemView(View):
    @auth_decorator
    def post(self, request, book_id, *args, **kwargs):
        book_item = get_object_or_404(
            BookItem,
            pk=book_id,
            account_id=self.request.session['account_id'],
            status=BookItem.STATUS.NOT_ACTIVE
        )
        book_item.status = BookItem.STATUS.ACTIVE
        book_item.save(update_fields=['status'])
        return JsonResponse({'success': True, 'book_id': book_item.id})


class DeactivateBookItemView(View):
    @auth_decorator
    def post(self, request, book_id, *args, **kwargs):
        book_item = get_object_or_404(
            BookItem,
            pk=book_id,
            account_id=self.request.session['account_id'],
            status=BookItem.STATUS.ACTIVE
        )
        book_item.status = BookItem.STATUS.NOT_ACTIVE
        book_item.save(update_fields=['status'])
        return JsonResponse({'success': True, 'book_id': book_item.id})


class DeleteBookView(View):
    @auth_decorator
    def post(self, request, book_id, *args, **kwargs):
        book_item = get_object_or_404(
            BookItem,
            pk=book_id,
            account_id=self.request.session['account_id'],
            status__in=[BookItem.STATUS.NOT_ACTIVE, BookItem.STATUS.ACTIVE]
        )

        book_item.status = BookItem.STATUS.DELETED
        book_item.save(update_fields=['status'])

        return JsonResponse({'success': True, 'book_id': book_item.id})
