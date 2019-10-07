import datetime
import os

from django.shortcuts import render, redirect
from django.views import View
from django.http.response import JsonResponse
from django.http import HttpResponse
from django.utils.timezone import make_aware

from apps.accounts.models import Account, VkSession
from apps.utils.auth import auth_decorator
from apps.vk_service.api import check_token


class VkRedirectUrl(View):
    def get(self, request):
        if request.session.get('vk_id') and request.session.get('access_token'):
            return redirect('app')
        return render(request, template_name='frontend/vk_redirect_url.html',
                      context={'root_url': os.getenv('ROOT_URL')})

    def post(self, request, *args, **kwargs):
        if request.session.get('vk_id') and request.session.get('access_token'):
            return redirect('app')

        access_token = request.POST.get('access_token')
        expires_in = request.POST.get('expires_in')
        vk_id = request.POST.get('user_id')
        if not (access_token and expires_in and vk_id) or not check_token(access_token, vk_id):
            return HttpResponse('Unauthorized', status=401)

        account, _ = Account.objects.get_or_create(vk_id=vk_id)
        expires_at = make_aware(datetime.datetime.now() + datetime.timedelta(seconds=int(expires_in)))
        vk_session = VkSession.objects.create(account=account, access_token=access_token, expires_at=expires_at)

        request.session.set_expiry(int(expires_in))
        request.session['vk_session_id'] = vk_session.id
        request.session['access_token'] = access_token
        request.session['account_id'] = account.id
        request.session['vk_id'] = vk_id

        return redirect('app')


class RootView(View):
    def get(self, request, *args, **kwargs):
        if request.session.get('vk_id') and request.session.get('access_token'):
            return redirect('app')
        else:
            return render(request, template_name='frontend/login_form.html',
                          context={'root_url': os.getenv('ROOT_URL'), 'vk_app_id': os.getenv('VK_APP_ID')})


class LogoutView(View):
    @auth_decorator
    def post(self, request, *args, **kwargs):
        del request.session['vk_session_id']
        del request.session['access_token']
        del request.session['account_id']
        del request.session['vk_id']

        return JsonResponse({'success': True})


class AppView(View):
    def get(self, request, *args, **kwargs):
        if request.session.get('vk_id') and request.session.get('access_token'):
            account = Account.objects.get(pk=request.session['account_id'])
            return render(request, template_name='frontend/app.html', context={'locale': account.locale})
        else:
            return redirect('login-form')
