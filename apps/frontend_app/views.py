from django.shortcuts import render, redirect
from django.views import View


class AppView(View):
    def get(self, request, *args, **kwargs):
        if request.session.get('vk_id') and request.session.get('access_token'):
            return render(request, template_name='frontend_app/app.html')
        else:
            return redirect(request, template_name='login-form')
