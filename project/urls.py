from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    url('', include('apps.frontend.urls')),
    url(r'app/api/my-books/', include('apps.books.urls.my_books')),
    url(r'app/api/friends-books/', include('apps.books.urls.friends_books')),
    url(r'app/api/book/', include('apps.books.urls.book')),
    url(r'app/api/settings/', include('apps.accounts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
