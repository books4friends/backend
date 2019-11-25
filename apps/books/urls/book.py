from django.conf.urls import url

from apps.books.views.book_detail import BookDetailView

urlpatterns = [
    url(r'(?P<book_id>\d+)/$', BookDetailView.as_view(), name='book-detail'),
]
