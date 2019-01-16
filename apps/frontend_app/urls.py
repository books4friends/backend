from django.conf.urls import url

from apps.frontend_app.views import AppView


urlpatterns = [
    url(r'^.*$', AppView.as_view(), name='app'),
]
