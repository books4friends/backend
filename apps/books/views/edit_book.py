from django.views import View

import json

from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404

from apps.utils.auth import auth_decorator

from ..models import Book
from ..forms import EditBookCommentForm


class EditBookCommentView(View):
    @auth_decorator
    def post(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(
            Book,
            pk=book_id,
            account_id=self.request.session['account_id'],
            status__in=[Book.STATUS.NOT_ACTIVE, Book.STATUS.ACTIVE]
        )

        data = json.loads(request.body.decode('utf-8'))
        form = EditBookCommentForm(data)
        if form.is_valid():
            book.comment = form.cleaned_data['comment']
            book.save(update_fields=['comment'])
            return JsonResponse({'success': True, 'book_id': book.id})
        else:
            return JsonResponse({'success': False, 'book_id': book.id})


class ActivateBookView(View):
    @auth_decorator
    def post(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(
            Book,
            pk=book_id,
            account_id=self.request.session['account_id'],
            status=Book.STATUS.NOT_ACTIVE
        )
        book.status = Book.STATUS.ACTIVE
        book.save(update_fields=['status'])
        return JsonResponse({'success': True, 'book_id': book.id})


class DeactivateBookView(View):
    @auth_decorator
    def post(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(
            Book,
            pk=book_id,
            account_id=self.request.session['account_id'],
            status=Book.STATUS.ACTIVE
        )
        book.status = Book.STATUS.NOT_ACTIVE
        book.save(update_fields=['status'])
        return JsonResponse({'success': True, 'book_id': book.id})


class DeleteBookView(View):
    @auth_decorator
    def post(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(
            Book,
            pk=book_id,
            account_id=self.request.session['account_id'],
            status__in=[Book.STATUS.NOT_ACTIVE, Book.STATUS.ACTIVE]
        )

        book.status = Book.STATUS.DELETED
        book.save(update_fields=['status'])

        return JsonResponse({'success': True, 'book_id': book.id})
