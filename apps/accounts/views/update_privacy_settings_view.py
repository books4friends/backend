from django.views import View

import json

from django.http.response import JsonResponse

from apps.utils.auth import auth_decorator

from ..models import Account, WhiteListOfFriendsLists
from ..forms import PrivacySomeFriends


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

