from django.views import View

import json
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.http import Http404

from apps.utils.auth import auth_decorator
from apps.books.models import Book
from apps.vk_service.api import get_friends_list
from .models import Borrow
from .forms import CreateBorrowFrom


class CreateBorrowView(View):
    @auth_decorator
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        form = CreateBorrowFrom(data)
        if not form.is_valid():
            return JsonResponse({'success': False, 'error_type': 'FORM_NOT_VALID', 'errors': form.errors})

        book = get_object_or_404(
            Book,
            pk=form.cleaned_data['book_id'],
            status=Book.STATUS.ACTIVE
        )

        if book.borrow_set.filter(real_return_date__isnull=True):
            return JsonResponse({'success': False, 'error_type': 'ALREADY_TAKEN'})

        friends = get_friends_list(request.session['access_token'])
        if book.account.vk_id not in [f['external_id'] for f in friends]:
            raise Http404('No Book matches the given query.')

        Borrow.objects.create(
            borrower_id=self.request.session['account_id'],
            book=book,
            planned_return_date=form.cleaned_data['planned_return_date']
        )

        return JsonResponse({'success': True})
