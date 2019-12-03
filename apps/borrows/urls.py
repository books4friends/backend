from django.conf.urls import url

from .views import CreateBorrowView, MyBorrowsListView

urlpatterns = [
    url(r'my/$', MyBorrowsListView.as_view(), name='my-borrows'),
    url(r'create/$', CreateBorrowView.as_view(), name='borrow-create'),
]
