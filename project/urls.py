from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url


urlpatterns = [
    path('admin/', admin.site.urls),
    url('', include('apps.frontend.urls')),
    url(r'^app/api/books/', include('apps.books.urls')),
    url(r'^app/api/settings/', include('apps.accounts.urls')),
]
