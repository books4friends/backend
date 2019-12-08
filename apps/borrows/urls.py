from django.conf.urls import url

from .views import CreateBorrowView, MyBorrowsListView, FriendsBorrowsListView, ReturnBorrowView, BorrowDetailView

urlpatterns = [
    url(r'my/$', MyBorrowsListView.as_view(), name='my-borrows'),
    url(r'friends/$', FriendsBorrowsListView.as_view(), name='my-borrows'),
    url(r'create/$', CreateBorrowView.as_view(), name='borrow-create'),
    url(r'(?P<borrow_id>\d+)/return/', ReturnBorrowView.as_view(), name='return-borrow'),
    url(r'(?P<borrow_id>\d+)/', BorrowDetailView.as_view(), name='borrow-detail'),
]
