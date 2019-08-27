from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    url('', include('apps.frontend.urls')),
    url(r'^app/api/books/', include('apps.books.urls')),
    url(r'^app/api/settings/', include('apps.accounts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
