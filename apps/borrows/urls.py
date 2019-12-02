from django.conf.urls import url

from .views import CreateBorrowView

urlpatterns = [
    url(r'create/$', CreateBorrowView.as_view(), name='borrow-create'),
]
