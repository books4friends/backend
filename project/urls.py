from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url


urlpatterns = [
    path('admin/', admin.site.urls),
    url('app/', include('apps.frontend_app.urls')),
    url('', include('apps.frontend.urls')),
]
