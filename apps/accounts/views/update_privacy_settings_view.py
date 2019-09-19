from django.views import View

import json

from django.http.response import JsonResponse

from apps.utils.auth import auth_decorator

from ..models import Account, FriendsWhiteList, FriendsBlackList
from ..forms import PrivacySomeFriends

from apps.vk_service.api import get_friends_list


class PrivacyFriendsListView(View):
    @auth_decorator
    def get(self, request, *args, **kwargs):
        friends = get_friends_list(request.session.get('access_token'))
        whitelist_friends = FriendsWhiteList.objects.\
            filter(owner=request.session['account_id']).\
            only('friend_ext_id')
        whitelist_friends = set(friend.friend_ext_id for friend in whitelist_friends)
        for friend in friends:
            friend['whitelist_selected'] = friend['external_id'] in whitelist_friends

        blacklist_friends = FriendsBlackList.objects.\
            filter(owner=request.session['account_id']).\
            only('friend_ext_id')
        blacklist_friends = set(friend.friend_ext_id for friend in blacklist_friends)
        for friend in friends:
            friend['blacklist_selected'] = friend['external_id'] in blacklist_friends

        return JsonResponse({'success': True, 'friends': friends})


class SetPrivacyAllFriendsView(View):
    @auth_decorator
    def post(self, request, *args, **kwargs):
        account = Account.objects.get(pk=request.session['account_id'])
        account.privacy_type = Account.PRIVACY_TYPE.ALL_FRIENDS
        account.save(update_fields=['privacy_type'])
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
            account.friendswhitelist_set.all().delete()
            FriendsWhiteList.objects.bulk_create(
                [FriendsWhiteList(owner=account, friend_ext_id=friend) for friend in friends]
            )
            account.privacy_type = Account.PRIVACY_TYPE.ONLY_SOME_FRIENDS
            account.save(update_fields=['privacy_type'])
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
            account.friendsblacklist_set.all().delete()
            FriendsBlackList.objects.bulk_create(
                [FriendsBlackList(owner=account, friend_ext_id=friend) for friend in friends]
            )
            account.privacy_type = Account.PRIVACY_TYPE.EXCEPT_SOME_FRIENDS
            account.save(update_fields=['privacy_type'])
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
        account.privacy_type = Account.PRIVACY_TYPE.ONLY_OWNER
        account.save(update_fields=['privacy_type'])
        return JsonResponse({
            'success': True
        })
