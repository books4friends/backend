from django.views import View

import json

from django.http.response import JsonResponse

from ..models import Account
from ..forms import LocaleForm
from apps.utils.auth import auth_decorator


class SetLocaleView(View):
    @auth_decorator
    def post(self, request, *args, **kwargs):
        account = Account.objects.get(pk=request.session['account_id'])

        data = json.loads(request.body.decode('utf-8'))
        form = LocaleForm(data)
        if form.is_valid():
            account.locale = form.cleaned_data['locale']
            account.save(update_fields=['locale'])
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})
