from django.views import View

import json
from django.http.response import JsonResponse
from django.utils import translation

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
            user_language = form.cleaned_data['locale']
            account.locale = user_language
            account.save(update_fields=['locale'])
            translation.activate(user_language)
            request.session[translation.LANGUAGE_SESSION_KEY] = user_language
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})
