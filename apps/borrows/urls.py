from django.conf.urls import url

from .views import CreateBorrowView, MyBorrowsListView, FriendsBorrowsListView

urlpatterns = [
    url(r'my/$', MyBorrowsListView.as_view(), name='my-borrows'),
    url(r'friends/$', FriendsBorrowsListView.as_view(), name='my-borrows'),
    url(r'create/$', CreateBorrowView.as_view(), name='borrow-create'),
]
