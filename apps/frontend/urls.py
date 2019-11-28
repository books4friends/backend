from django.conf.urls import url
from django.views.generic import TemplateView

from apps.frontend.views import VkRedirectUrl, LogoutView, RootView
from .views import AppView


urlpatterns = [
    url(r'^vk_redirect_uri/$', VkRedirectUrl.as_view(), name='vk-redirect-uri'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^$', RootView.as_view(), name='login-form'),
    url(r'^app/$', AppView.as_view(), name='app'),
    url(r'^app/.*/$', AppView.as_view(), name='app-my_books'),
]