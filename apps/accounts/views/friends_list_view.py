from django.views import View

from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404

from apps.utils.auth import auth_decorator
from apps.vk_service.api import get_friends_list

from ..models import WhiteListOfFriendsLists, BlackListOfFriendsLists


class FriendsListView(View):
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
