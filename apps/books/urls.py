from django.conf.urls import url
from .views.add_book import AddBookView


urlpatterns = [
    url(r'^add-book/$', AddBookView.as_view(), name='add-books'),
]
