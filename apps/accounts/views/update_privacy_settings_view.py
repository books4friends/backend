from django.views import View

import json

from django.http.response import JsonResponse

from apps.utils.auth import auth_decorator

from ..models import Account, WhiteListOfFriendsLists, BlackListOfFriendsLists
from ..forms import PrivacySomeFriends

from apps.vk_service.api import get_friends_list


class PrivacyFriendsListView(View):
    @auth_decorator
    def get(self, request, *args, **kwargs):
        friends = get_friends_list(request.session.get('access_token'))
        whitelist_friends = WhiteListOfFriendsLists.objects.\
            filter(owner_id=request.session['account_id']).\
            only('friend_id')
        whitelist_friends = set(friend.friend_id for friend in whitelist_friends)
        for friend in friends:
            friend['whitelist_selected'] = friend['external_id'] in whitelist_friends

        blacklist_friends = BlackListOfFriendsLists.objects.\
            filter(owner_id=request.session['account_id']).\
            only('friend_id')
        blacklist_friends = set(friend.friend_id for friend in blacklist_friends)
        for friend in friends:
            friend['blacklist_selected'] = friend['external_id'] in blacklist_friends

        return JsonResponse({'success': True, 'friends': friends})


class SetPrivacyAllFriendsView(View):
    @auth_decorator
    def post(self, request, *args, **kwargs):
        account = Account.objects.get(pk=request.session['account_id'])
        account.visibility_type = Account.VISIBILITY_TYPE.ALL_FRIENDS
        account.save(update_fields=['visibility_type'])
        return JsonResponse({
            'success': True
        })


class SetPrivacySomeFriendsView(View):
    @auth_decorator
    def post(self, request, *args, **kwargs):
        account = Account.objects.get(pk=request.session['account_id'])
        data = json.loads(request.body.decode('utf-8'))
        form = PrivacySomeFriends(data)
        if form.is_valid():
            friends = form.cleaned_data['selected_friends']
            account.whitelistoffriendslists_set.all().delete()
            WhiteListOfFriendsLists.objects.bulk_create(
                [WhiteListOfFriendsLists(owner_id=account, friend_id=friend) for friend in friends]
            )
            account.visibility_type = Account.VISIBILITY_TYPE.ONLY_SOME_FRIENDS
            account.save(update_fields=['visibility_type'])
            return JsonResponse({
                'success': True
            })

        else:
            return JsonResponse({
                'success': False
            })


class SetPrivacyExceptSomeFriendsView(View):
    @auth_decorator
    def post(self, request, *args, **kwargs):
        account = Account.objects.get(pk=request.session['account_id'])
        data = json.loads(request.body.decode('utf-8'))
        form = PrivacySomeFriends(data)
        if form.is_valid():
            friends = form.cleaned_data['selected_friends']
            account.blacklistoffriendslists_set.all().delete()
            BlackListOfFriendsLists.objects.bulk_create(
                [BlackListOfFriendsLists(owner_id=account, friend_id=friend) for friend in friends]
            )
            account.visibility_type = Account.VISIBILITY_TYPE.EXCEPT_SOME_FRIENDS
            account.save(update_fields=['visibility_type'])
            return JsonResponse({
                'success': True
            })

        else:
            return JsonResponse({
                'success': False
            })


class SetPrivacyOnlyOwnerView(View):
    @auth_decorator
    def post(self, request, *args, **kwargs):
        account = Account.objects.get(pk=request.session['account_id'])
        account.visibility_type = Account.VISIBILITY_TYPE.ONLY_OWNER
        account.save(update_fields=['visibility_type'])
        return JsonResponse({
            'success': True
        })
