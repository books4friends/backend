from django.conf.urls import url

from apps.books.views.friends_books import GetFiltersView, GetFriendsBooksListView

urlpatterns = [
    url(r'^$', GetFriendsBooksListView.as_view(), name='friends-books-list'),
    url(r'get-filters/', GetFiltersView.as_view(), name='friends-books-filters'),
]
