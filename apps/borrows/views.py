from django.views import View

import json
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.http import Http404

from apps.books.serializers import BookSerializer
from apps.utils.auth import auth_decorator
from apps.books.models import Book
from apps.vk_service.api import get_friends_list, get_users_info
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


class MyBorrowsListView(View):
    @auth_decorator
    def get(self, request, *args, **kwargs):
        account_id = request.session['account_id']
        borrows = Borrow.objects.filter(borrower=account_id).order_by('real_return_date').\
            prefetch_related('book', 'book__account')
        friends_ids = [borrow.book.account.vk_id for borrow in borrows]
        friends = get_users_info(request.session['access_token'], friends_ids)

        return JsonResponse(self._serialize_borrows(borrows, friends))

    def _serialize_borrows(self, borrows, friends):
        friends_dict = {friend['external_id']: friend for friend in friends}
        return {
            "borrows": [{
                "id": borrow.pk,
                "owner": friends_dict[borrow.book.account.vk_id],
                "book": BookSerializer.serialize(borrow.book),
                "borrow_data": {
                    "take_date": borrow.take_date,
                    "planned_return_date": borrow.planned_return_date,
                    "real_return_date": borrow.real_return_date,
                }
            } for borrow in borrows]
        }
