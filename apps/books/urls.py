from django.conf.urls import url

from .views.add_book import AddBookView
from .views.my_books_list import MyBooksList
from .views.delete_book_view import DeleteBookView


urlpatterns = [
    url(r'^add-book/$', AddBookView.as_view(), name='add-books'),
    url(r'^my-books/$', MyBooksList.as_view(), name='my-books'),
    url(r'^my-books/(?P<book_id>\d+)/delete/$', DeleteBookView.as_view(), name='delete-my-book'),
]
