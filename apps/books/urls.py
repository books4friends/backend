from django.conf.urls import url

from .views.add_book import AddBookView
from .views.my_books_list import MyBooksList
from .views.delete_book_view import DeleteBookView
from .views.edit_book_item import EditBookItemCommentView, ActivateBookItemView, DeactivateBookItemView
from .views.friends_books import GetFiltersView, GetFriendsBooksListView

urlpatterns = [
    url(r'^add-book/$', AddBookView.as_view(), name='add-books'),
    url(r'^my-books/$', MyBooksList.as_view(), name='my-books'),
    url(r'^my-books/(?P<book_id>\d+)/delete/$', DeleteBookView.as_view(), name='delete-my-book'),
    url(r'^my-books/(?P<book_id>\d+)/edit-comment/$', EditBookItemCommentView.as_view(),
        name='edit-comment-of-my-book'),
    url(r'^my-books/(?P<book_id>\d+)/activate/$', ActivateBookItemView.as_view(),
        name='activate-my-book'),
    url(r'^my-books/(?P<book_id>\d+)/deactivate/$', DeactivateBookItemView.as_view(),
        name='deactivate-my-book'),

    url(r'friends-books/get-filters/', GetFiltersView.as_view(), name='friends-books-filters'),
    url(r'friends-books/get-books/', GetFriendsBooksListView.as_view(), name='friends-books-list')
]
