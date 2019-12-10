from django.views import View

import json
import datetime
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.http import Http404

from apps.utils.auth import auth_decorator
from apps.books.models import Book
from apps.vk_service.api import get_friends_list, get_users_info, get_user_info
from .models import Borrow
from .forms import CreateBorrowFrom
from .serializers import MyBorrowsSerializer, FriendBorrowsSerializer


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

        if book.borrow_set.filter(real_return_date__isnull=True, status__in=[Borrow.STATUS.NEW, Borrow.STATUS.Approve]):
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
        borrows = Borrow.objects.filter(borrower=account_id, status__in=Borrow.VISIBLE_STATUSES).\
            prefetch_related('book', 'book__account')
        friends_ids = [borrow.book.account.vk_id for borrow in borrows]
        friends = get_users_info(request.session['access_token'], friends_ids)

        return JsonResponse({'borrows': MyBorrowsSerializer.serialize(borrows, friends)})


class FriendsBorrowsListView(View):
    @auth_decorator
    def get(self, request, *args, **kwargs):
        account_id = request.session['account_id']
        borrows = Borrow.objects.filter(book__account_id=account_id, status__in=Borrow.VISIBLE_STATUSES).\
            prefetch_related('book')
        friends_ids = [borrow.borrower.vk_id for borrow in borrows]
        friends = get_users_info(request.session['access_token'], friends_ids)

        return JsonResponse({'borrows': FriendBorrowsSerializer.serialize(borrows, friends)})


class BorrowDetailView(View):
    @auth_decorator
    def get(self, request, borrow_id, *args, **kwargs):
        account_id = request.session['account_id']
        borrow = get_object_or_404(
            Borrow,
            pk=borrow_id,
            status__in=Borrow.VISIBLE_STATUSES
        )

        if borrow.borrower_id == account_id:
            friend = get_user_info(request.session['access_token'], borrow.book.account.vk_id)
            return JsonResponse({
                'borrow': MyBorrowsSerializer.serialize(borrow, friend),
                'owner_type': 'friend'
            })

        if borrow.book.account_id == account_id:
            friend = get_user_info(request.session['access_token'], borrow.borrower.vk_id)
            return JsonResponse({
                'borrow': FriendBorrowsSerializer.serialize(borrow, friend),
                'owner_type': 'self'
            })

        raise Http404('No Borrow matches the given query.')


class ApproveBorrowView(View):
    @auth_decorator
    def post(self, request, borrow_id, *args, **kwargs):
        borrow = get_object_or_404(
            Borrow,
            pk=borrow_id,
            status=Borrow.STATUS.NEW,
            book__account_id=request.session['account_id'],
        )
        borrow.status = Borrow.STATUS.Approve
        borrow.save(update_fields=['status'])
        return JsonResponse({'success': True})


class CancelBorrowView(View):
    @auth_decorator
    def post(self, request, borrow_id, *args, **kwargs):
        borrow = get_object_or_404(
            Borrow,
            pk=borrow_id,
            status=Borrow.STATUS.NEW,
            borrower_id=request.session['account_id'],
        )
        borrow.status = Borrow.STATUS.CANCELED
        borrow.save(update_fields=['status'])
        return JsonResponse({'success': True})


class RejectBorrowView(View):
    @auth_decorator
    def post(self, request, borrow_id, *args, **kwargs):
        borrow = get_object_or_404(
            Borrow,
            pk=borrow_id,
            status=Borrow.STATUS.NEW,
            book__account_id=request.session['account_id'],
        )
        borrow.status = Borrow.STATUS.REJECTED
        borrow.save(update_fields=['status'])
        return JsonResponse({'success': True})


class ReturnBorrowView(View):
    @auth_decorator
    def post(self, request, borrow_id, *args, **kwargs):
        borrow = get_object_or_404(
            Borrow,
            pk=borrow_id,
            book__account_id=request.session['account_id'],
            status=Borrow.STATUS.Approve,
        )

        borrow.status = Borrow.STATUS.RETURNED
        borrow.real_return_date = datetime.date.today()
        borrow.save(update_fields=['real_return_date', 'status'])
        return JsonResponse({'success': True})
