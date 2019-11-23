from django.conf.urls import url

from apps.books.views.add_book import AddMyBookView
from apps.books.views.my_books_list import MyBooksList
from apps.books.views.edit_book import EditBookCommentView, ActivateBookView, DeactivateBookView, \
    DeleteBookView

urlpatterns = [
    url(r'^$', MyBooksList.as_view(), name='my-books'),
    url(r'^add/$', AddMyBookView.as_view(), name='add-books'),
    url(r'(?P<book_id>\d+)/delete/$', DeleteBookView.as_view(), name='delete-my-book'),
    url(r'(?P<book_id>\d+)/edit-comment/$', EditBookCommentView.as_view(),
        name='edit-comment-of-my-book'),
    url(r'(?P<book_id>\d+)/activate/$', ActivateBookView.as_view(),
        name='activate-my-book'),
    url(r'(?P<book_id>\d+)/deactivate/$', DeactivateBookView.as_view(),
        name='deactivate-my-book'),
]
