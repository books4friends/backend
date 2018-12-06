from django.conf.urls import url
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^app/$', TemplateView.as_view(template_name='frontend/main.html'), name='main'),
]