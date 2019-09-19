from django.views import View

from django.http.response import JsonResponse

from apps.utils.auth import auth_decorator

from ..models import Account


class AccountSettingsView(View):
    @auth_decorator
    def get(self, request, *args, **kwargs):
        account = Account.objects.get(pk=request.session['account_id'])
        return JsonResponse({
            'visibility_type': account.privacy_type
        })
