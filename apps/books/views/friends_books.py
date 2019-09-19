from django.views import View

import uuid
import re
import operator
from functools import reduce
from constance import config

from django.db.models import Q, F, Value
from django.db.models.functions import Concat
from django.core.cache import cache
from django.http.response import JsonResponse

from apps.utils.auth import auth_decorator

from ..models import BookItem
from ...vk_service.api import get_friends_list
from ...accounts.models import Account


def friends_decorator(function):
    def _create_friends_list(session):
        friends = get_friends_list(session['access_token'])
        friends_ids = [f['external_id'] for f in friends]
        all_friends = Account.objects.filter(
            vk_id__in=friends_ids,
            privacy_type=Account.PRIVACY_TYPE.ALL_FRIENDS
        ).exclude(bookitem__isnull=True).values('id', 'vk_id')

        whitelist_friends = Account.objects.filter(
            vk_id__in=friends_ids,
            privacy_type=Account.PRIVACY_TYPE.ONLY_SOME_FRIENDS,
            friendswhitelist__friend_ext_id=session['vk_id']
        ).exclude(bookitem__isnull=True).values('id', 'vk_id')

        blacklist_friends = Account.objects.filter(
            vk_id__in=friends_ids,
            privacy_type=Account.PRIVACY_TYPE.EXCEPT_SOME_FRIENDS
        ).exclude(
            friendsblacklist__friend_ext_id=session['vk_id']
        ).exclude(
            bookitem__isnull=True
        ).values('id', 'vk_id')

        filtered_friends = list(all_friends) + list(whitelist_friends) + list(blacklist_friends)
        filtered_friends = {f['vk_id']: f['id'] for f in filtered_friends}
        friends_list = []
        for friend in friends:
            if friend['external_id'] in filtered_friends:
                friend['account_id'] = filtered_friends[friend['external_id']]
                friends_list.append(friend)
        return friends_list

    def wrap(self, request, *args, **kwargs):
        token = request.GET.get('token')
        account_id = request.GET.get('account_id')
        key = "{}_{}".format(token, account_id)
        if not token or not cache.has_key(key):
            friends_list = _create_friends_list(request.session)
            token = uuid.uuid4()
            key = "{}_{}".format(token, account_id)
            cache.set(key, friends_list, timeout=config.CASH_TOKEN_TIMEOUT)
        else:
            friends_list = cache.get(key)

        response = function(self, request, friends_list, *args, **kwargs)
        if isinstance(response, dict):
            return JsonResponse({
                'data': response,
                'token': token
            })
        else:
            return response

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


class GetFiltersView(View):
    @auth_decorator
    @friends_decorator
    def get(self, request, friends_list, *args, **kwargs):
        return {
            'friends': friends_list,
            'cities': self._generate_cities_list(friends_list)
        }

    @classmethod
    def _generate_cities_list(cls, friends_list):
        cities = {}
        for friend in friends_list:
            if friend['city'] is not None:
                if not friend['city']['id'] in cities:
                    cities[friend['city']['id']] = {
                        'id': friend['city']['id'],
                        'title': friend['city']['title'],
                        'count': 0
                    }
                cities[friend['city']['id']]['count'] += 1
        cities = sorted(list(cities.values()), key=lambda c: c['count'], reverse=True)
        return cities


class GetFriendsBooksListView(View):
    @auth_decorator
    @friends_decorator
    def get(self, request, friends_list, *args, **kwargs):
        if request.GET.get('city'):
            friends_list = self.filter_friends_by_city(friends_list, int(request.GET.get('city')))
        if request.GET.get('friend'):
            friends_list = self.filter_friends_by_friend(friends_list, int(request.GET.get('friend')))

        books = BookItem.objects.filter(
            account__in=[friend['account_id'] for friend in friends_list]
        ).prefetch_related('detail')

        if request.GET.get('search'):
            keywords = re.findall(r'\b\w+\b', request.GET.get('search'))
            keywords = [keyword.lower() for keyword in keywords]
            books = books.annotate(title_and_author=Concat(F('detail__title'), Value(' '), F('detail__author')))
            query = reduce(operator.and_, (Q(title_and_author__icontains=item) for item in keywords))
            books = books.filter(query)

        offset = request.GET.get('offset', 0)
        offset = int(offset)
        count = request.GET.get('count', config.BOOKS_AMOUNT_PER_PAGE)
        books = books[offset: offset+count]

        return self._serialize_books(books, friends_list)

    @classmethod
    def filter_friends_by_city(cls, friends, city_id):
        return [friend for friend in friends if friend['city'] and friend['city']['id'] == city_id]

    @classmethod
    def filter_friends_by_friend(cls, friends, friend_ext_id):
        return [friend for friend in friends if friend['account_id'] == friend_ext_id]

    @classmethod
    def _serialize_books(cls, books, friends):
        friends_dict = {friend['account_id']: friend for friend in friends}
        return {
            "books": [{
                "owner": friends_dict[book.account_id],
                "description": {
                    "title": book.detail.title,
                    "author": book.detail.author,
                    "image": book.detail.image.url if book.detail.image.name else None,
                },
                "comment": book.comment
            } for book in books]
        }

