from django.views import View

import json

from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.http import Http404

from apps.utils.auth import auth_decorator

from ..models import Book
from ..serializers import BookSerializer
from ...vk_service.api import get_friends_list, get_user_info


class BookDetailView(View):
    @auth_decorator
    def get(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(
            Book,
            pk=book_id,
            status__in=[Book.STATUS.NOT_ACTIVE, Book.STATUS.ACTIVE]
        )

        if book.account_id == self.request.session['account_id']:
            return JsonResponse({
                'book': BookSerializer.serialize(book),
                'owner_type': 'self',
                'owner': get_user_info(request.session['access_token'])
            })

        friends = get_friends_list(request.session['access_token'])
        if book.account.vk_id in [f['external_id'] for f in friends] and book.status == Book.STATUS.ACTIVE:
            friends_dict = {friend['external_id']: friend for friend in friends}
            return JsonResponse({
                'book': BookSerializer.serialize(book),
                'owner_type': 'friend',
                'owner': friends_dict[book.account.vk_id]
            })

        raise Http404('No Book matches the given query.')
